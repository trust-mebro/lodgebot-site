document.getElementById('fileUpload').addEventListener('change', function () {
  const file = this.files[0];
  const output = document.getElementById('output');

  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    const text = e.target.result;
    output.innerHTML = formatFields(text);
  };
  reader.readAsText(file);
});

function formatFields(text) {
  const lines = text.split('\n').filter(line => line.includes(':'));
  if (!lines.length) return '<div class="no-fields">No known fields found.</div>';

  let html = '<div class="field-list">';

  lines.forEach(line => {
    const [key, ...rest] = line.split(':');
    const value = rest.join(':').trim(); // handle colons inside values

    html += `
      <div class="field">
        <span class="label">${key.trim()}:</span>
        <span class="value">${value}</span>
      </div>
    `;
  });

  html += '</div>';
  return html;
}
