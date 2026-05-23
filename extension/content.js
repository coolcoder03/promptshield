function getPromptBox() {
  return (
    document.querySelector("#prompt-textarea") ||
    document.querySelector('[contenteditable="true"]') ||
    document.querySelector("textarea")
  );
}

function getPromptText(box) {
  return (
    box.innerText ||
    box.textContent ||
    box.value ||
    ""
  ).trim();
}

function setPromptText(box, text) {
  box.focus();

  if (box.tagName.toLowerCase() === "textarea") {
    box.value = text;
    box.dispatchEvent(new Event("input", { bubbles: true }));
  } else {
    box.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = text;
    box.appendChild(p);

    box.dispatchEvent(new InputEvent("input", {
      bubbles: true,
      inputType: "insertText",
      data: text
    }));
  }
}

function injectPromptShield() {
  if (document.getElementById("promptshield-root")) return;

  const root = document.createElement("div");
  root.id = "promptshield-root";

  root.innerHTML = `<button id="promptshield-btn">🛡 Enhance Prompt</button>`;
  document.body.appendChild(root);

  const btn = document.getElementById("promptshield-btn");

  btn.onclick = async () => {
    const box = getPromptBox();

    if (!box) {
      alert("Prompt box not found.");
      return;
    }

    const prompt = getPromptText(box);
    console.log("PromptShield detected prompt:", prompt);

    if (!prompt) {
      alert("Type a prompt first.");
      return;
    }

    btn.innerText = "Improving...";

    try {
      const res = await fetch("http://localhost:8000/enhance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, mode: "general" }),
      });

      const data = await res.json();

      setPromptText(box, data.enhanced_prompt);

      btn.innerText =
        data.provider_status === "gateway_success"
          ? "✅ Enhanced"
          : "⚠ Fallback Used";
    } catch (err) {
      console.error("PromptShield error:", err);
      btn.innerText = "❌ Backend Error";
    }

    setTimeout(() => {
      btn.innerText = "🛡 Enhance Prompt";
    }, 2500);
  };
}

injectPromptShield();

new MutationObserver(() => injectPromptShield()).observe(document.body, {
  childList: true,
  subtree: true,
});