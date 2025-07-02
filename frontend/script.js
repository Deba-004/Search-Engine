async function search() {
  const query = document.getElementById("query").value;
  const difficulty = document.getElementById("difficulty").value;
  const language = document.getElementById("language").value;

  const res = await fetch('http://localhost:5000/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, difficulty, language })
  });

  const data = await res.json();
  const resultsEl = document.getElementById("results");
  resultsEl.innerHTML = "";
  data.forEach(p => {
    const li = document.createElement("li");
    li.innerHTML = `<a href="${p.link}" target="_blank">${p.title}</a> [${p.difficulty}]`;
    resultsEl.appendChild(li);
  });
}