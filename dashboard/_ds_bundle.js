/* @ds-bundle: window.VasyaDS — Button, Card, ProgressBar, Quote, SectionHeading, Stat, Tag */
/**
 * VASYA DS — component bundle exposed as window.VasyaDS.
 * Plain React.createElement, no JSX build step required.
 */
(function () {
  const e = React.createElement;

  function SectionHeading({ tag, title }) {
    return e("div", { className: "vds-section-heading" }, [
      tag && e("div", { key: "tag", className: "vds-tag-label" }, tag),
      e("h1", { key: "title", className: "vds-title" }, title),
    ]);
  }

  function Stat({ numeral, label }) {
    return e("div", { className: "vds-stat" }, [
      e("div", { key: "n", className: "vds-stat-numeral" }, numeral),
      e("div", { key: "l", className: "vds-stat-label" }, label),
    ]);
  }

  function Card({ tone = "violet", num, title, formula, children }) {
    return e("div", { className: `vds-card vds-tone-${tone}` }, [
      num && e("div", { key: "num", className: "vds-card-num" }, num),
      title && e("h3", { key: "title", className: "vds-card-title" }, title),
      formula && e("code", { key: "formula", className: "vds-card-formula" }, formula),
      children && e("p", { key: "body", className: "vds-card-body" }, children),
    ]);
  }

  function ProgressBar({ percent = 0, label, caption }) {
    const clamped = Math.max(0, Math.min(100, percent));
    return e("div", { className: "vds-progress" }, [
      label && e("div", { key: "label", className: "vds-progress-label" }, label),
      e(
        "div",
        { key: "track", className: "vds-progress-track" },
        e("div", { className: "vds-progress-fill", style: { width: `${clamped}%` } })
      ),
      caption && e("div", { key: "caption", className: "vds-progress-caption" }, caption),
    ]);
  }

  function Button({ variant = "primary", href, onClick, children }) {
    return e(
      "a",
      { className: `vds-btn vds-btn-${variant}`, href: href || "#", onClick },
      children
    );
  }

  function Tag({ tone = "default", children }) {
    return e("span", { className: `vds-tag vds-tag-${tone}` }, children);
  }

  function Quote({ children }) {
    return e("blockquote", { className: "vds-quote" }, children);
  }

  window.VasyaDS = { SectionHeading, Stat, Card, ProgressBar, Button, Tag, Quote };
})();
