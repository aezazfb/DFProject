function runTool(tool) {
  console.log("🚀 runTool called for:", tool);  // Debug log
  const value = document.getElementById('domain').value;
  const output = document.getElementById('output');
  output.innerText = 'Running...\n';

  fetch(`http://127.0.0.1:5000/${tool}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(tool === 'mosint' ? { email: value } : { domain: value })
  })
    .then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      function read() {
        reader.read().then(({ done, value }) => {
          if (done) return;
          output.innerText += decoder.decode(value);
          read();
        });
      }
      read();
    })
    .catch(err => {
      output.innerText = 'Error: ' + err;
    });
}

// Event listeners for buttons
document.getElementById('knockBtn').addEventListener('click', () => runTool('knock'));
document.getElementById('dnsenumBtn').addEventListener('click', () => runTool('dnsenum'));
document.getElementById('mosintBtn').addEventListener('click', () => runTool('mosint'));
