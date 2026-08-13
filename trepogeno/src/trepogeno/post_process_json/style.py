def style_html(html_path):
    # Inject filter UI and JS into the HTML file
    filter_html = """
    <label for="supportFilter">Filter by Total support (≥ %): </label>
    <input type="number" id="supportFilter" value="0" min="0" max="100" step="1" />

    <label for="sampleFilter" style="margin-left: 20px;">Filter by Sample ID: </label>
    <input type="text" id="sampleFilter" placeholder="Enter Sample ID" />

    <label for="lineageFilter" style="margin-left: 20px;">Filter by Lineage: </label>
    <input type="text" id="lineageFilter" placeholder="Enter Lineage" />

    <button onclick="filterTable()">Apply Filter</button>

    <script>
    function filterTable() {
        const supportInput = document.getElementById("supportFilter");
        const sampleInput = document.getElementById("sampleFilter");
        const lineageInput = document.getElementById("lineageFilter");

        const supportFilter = parseFloat(supportInput.value) || 0;
        const sampleFilter = sampleInput.value.toLowerCase();
        const lineageFilter = lineageInput.value.toLowerCase();
        
        const table = document.querySelector("table");
        const rows = table.querySelectorAll("tbody tr");

        rows.forEach(row => {
            const supportCell = row.cells[4];  // "Total support"
            const sampleCell = row.cells[0];   // "Sample ID"
            const lineageCell = row.cells[1]; // "Lineage"

            const supportValue = parseFloat(supportCell.textContent);
            const sampleID = sampleCell.textContent.toLowerCase();
            const lineageName = lineageCell.textContent.toLowerCase();

            const supportCondition = supportValue >= supportFilter;
            const sampleCondition = sampleID.includes(sampleFilter);
            const lineageCondition = lineageName.includes(lineageFilter)

            if (supportCondition && sampleCondition && lineageCondition) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    }
    </script>
    """

    # Read the saved HTML file
    with open(html_path, 'r') as file:
        html_content = file.read()

    # Insert the filter UI before </body> or at the end if no </body> tag
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', filter_html + '</body>')
    else:
        html_content += filter_html

    # Write back the updated HTML
    with open(html_path, 'w') as file:
        file.write(html_content)
