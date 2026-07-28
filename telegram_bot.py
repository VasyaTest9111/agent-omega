import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from github_client import GitHubClient
from gemini_client import GeminiClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GITHUB_OWNER = os.getenv("GITHUB_OWNER", "VasyaTest9111")

github = GitHubClient()
gemini = GeminiClient()


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
    await update.message.reply_text("🤖 Думаю...")

    # Дай GitHub контекст якщо питання пов'язане з репо
    github_context = None
    keywords = ["репо", "repo", "гілк", "branch", "коміт", "commit", "pr", "issue", "код", "code", "github"]
    if any(kw in user_text.lower() for kw in keywords):
        github_context = github.get_repo_summary(GITHUB_OWNER, "agent-omega")

    response = gemini.ask(user_text, github_context)
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
