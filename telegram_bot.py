import os
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from github_client import GitHubClient
from gemini_client import GeminiClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GITHUB_OWNER = os.getenv("OWNER_M", "VasyaTest9111")
GITHUB_CONTEXT_TTL_SECONDS = 300  # re-fetch repo summary at most every 5 minutes per chat
HISTORY_TURNS = 6  # how many past exchanges to keep per chat

github = GitHubClient()
gemini = GeminiClient()


@dataclass
class ChatSession:
    """Per-chat memory so GitHub context and conversation history survive between messages."""
    github_context: Optional[str] = None
    github_context_fetched_at: float = 0.0
    history: List[str] = field(default_factory=list)

    def cached_github_context(self) -> Optional[str]:
        if self.github_context and (time.time() - self.github_context_fetched_at) < GITHUB_CONTEXT_TTL_SECONDS:
            return self.github_context
        return None

    def store_github_context(self, context: str):
        self.github_context = context
        self.github_context_fetched_at = time.time()

    def add_turn(self, user_text: str, bot_text: str):
        self.history.append(f"Користувач: {user_text}\nAgent Omega: {bot_text}")
        self.history = self.history[-HISTORY_TURNS:]


SESSIONS: Dict[int, ChatSession] = {}


def get_session(chat_id: int) -> ChatSession:
    if chat_id not in SESSIONS:
        SESSIONS[chat_id] = ChatSession()
    return SESSIONS[chat_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привіт! Я Agent Omega з доступом до GitHub + Gemini AI.\n\n"
        "Команди:\n"
        "/repos — мої репозиторії\n"
        "/branches [repo] — гілки репо\n"
        "/commits [repo] — останні коміти\n"
        "/prs [repo] — відкриті PR\n"
        "/issues [repo] — відкриті issues\n"
        "/summary [repo] — повний огляд репо\n\n"
        "Або просто пиши — відповім через Gemini AI 🤖"
    )


async def repos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo_list = github.list_repos()
    if not repo_list:
        await update.message.reply_text("❌ Не вдалось отримати репо (перевір GITHUB_TOKEN)")
        return

    lines = ["📁 *Твої репозиторії:*\n"]
    for r in repo_list:
        icon = "🔒" if r["private"] else "🌐"
        lang = f" [{r['language']}]" if r["language"] else ""
        lines.append(f"{icon} `{r['name']}`{lang}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def branches(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.args[0] if context.args else "agent-omega"
    result = github.list_branches(GITHUB_OWNER, repo)
    if not result:
        await update.message.reply_text(f"❌ Не знайдено гілок у {repo}")
        return
    text = f"🌿 *Гілки {repo}:*\n" + "\n".join(f"  • `{b}`" for b in result)
    await update.message.reply_text(text, parse_mode="Markdown")


async def commits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.args[0] if context.args else "agent-omega"
    result = github.list_commits(GITHUB_OWNER, repo)
    if not result:
        await update.message.reply_text(f"❌ Не знайдено комітів у {repo}")
        return
    lines = [f"📝 *Останні коміти {repo}:*\n"]
    for c in result:
        lines.append(f"`{c['sha']}` {c['message']}\n  _{c['author']}_ · {c['date']}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def prs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.args[0] if context.args else "agent-omega"
    result = github.list_pull_requests(GITHUB_OWNER, repo)
    if not result:
        await update.message.reply_text(f"✅ Немає відкритих PR у {repo}")
        return
    lines = [f"🔀 *Відкриті PR {repo}:*\n"]
    for p in result:
        lines.append(f"#{p['number']} {p['title']} (@{p['author']}) `{p['branch']}`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.args[0] if context.args else "agent-omega"
    result = github.list_issues(GITHUB_OWNER, repo)
    if not result:
        await update.message.reply_text(f"✅ Немає відкритих issues у {repo}")
        return
    lines = [f"🐛 *Відкриті Issues {repo}:*\n"]
    for i in result:
        lines.append(f"#{i['number']} {i['title']} (@{i['author']})")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    repo = context.args[0] if context.args else "agent-omega"
    await update.message.reply_text(f"⏳ Збираю інфо про {repo}...")
    text = github.get_repo_summary(GITHUB_OWNER, repo)
    await update.message.reply_text(f"```\n{text}\n```", parse_mode="Markdown")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    session = get_session(update.effective_chat.id)
    await update.message.reply_text("🤖 Думаю...")

    # GitHub-контекст: береться зі свіжого кешу чату, якщо він є, інакше запитується заново
    github_context = session.cached_github_context()
    keywords = ["репо", "repo", "гілк", "branch", "коміт", "commit", "pr", "issue", "код", "code", "github"]
    if github_context is None and any(kw in user_text.lower() for kw in keywords):
        github_context = github.get_repo_summary(GITHUB_OWNER, "agent-omega")
        session.store_github_context(github_context)

    response = gemini.ask(user_text, github_context, history=session.history)
    session.add_turn(user_text, response)
    await update.message.reply_text(response)


def main():
    token = os.getenv("TELEGRAM_TOKEN_1")
    if not token:
        logger.error("TELEGRAM_TOKEN_1 не встановлено у .env")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("repos", repos))
    app.add_handler(CommandHandler("branches", branches))
    app.add_handler(CommandHandler("commits", commits))
    app.add_handler(CommandHandler("prs", prs))
    app.add_handler(CommandHandler("issues", issues))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🚀 Agent Omega Telegram Bot запущено")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
