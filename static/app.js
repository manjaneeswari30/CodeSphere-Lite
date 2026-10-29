
document.addEventListener("DOMContentLoaded", () => {
  const codeEditor = document.getElementById("code");
  const runBtn = document.getElementById("runBtn");
  const outputBox = document.getElementById("output");
  const statusBox = document.getElementById("status");
  const inputBox = document.getElementById("input");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");

  async function runCode(event) {
    if (event) {
      event.preventDefault();
    }

    if (!codeEditor || !outputBox || !runBtn) {
      console.error("Missing code editor, output box, or Run Code button.");
      return;
    }

    const code = codeEditor.value;
    const input = inputBox ? inputBox.value : "";

    runBtn.disabled = true;
    runBtn.textContent = "Running...";
    outputBox.textContent = "Running your Python code...";

    if (statusBox) {
      statusBox.textContent = "Executing";
    }

    try {
      const response = await fetch("/run", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ code, input })
      });

      const data = await response.json();

      outputBox.textContent =
        data.output || data.error || "Program finished with no output.";

      if (statusBox) {
        statusBox.textContent = response.ok && data.success
          ? "Success"
          : "Error";
      }
    } catch (error) {
      outputBox.textContent =
        "Could not connect to the server. Make sure Flask is running.";

      if (statusBox) {
        statusBox.textContent = "Connection Error";
      }

      console.error(error);
    } finally {
      runBtn.disabled = false;
      runBtn.textContent = "Run Code";
    }
  }

  if (runBtn) {
    runBtn.addEventListener("click", runCode);
  }

  const runForm = document.getElementById("runForm");

  if (runForm) {
    runForm.addEventListener("submit", runCode);
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener("click", async () => {
      if (!window.confirm("Clear all recent run history?")) {
        return;
      }

      try {
        const response = await fetch("/clear-history", {
          method: "POST"
        });

        if (response.ok) {
          window.location.reload();
        } else {
          window.alert("Unable to clear history.");
        }
      } catch (error) {
        window.alert("Unable to clear history. Check the Flask server.");
      }
    });
  }
});
