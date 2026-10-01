/**
 * Receives applications from web/apply.html and appends them to the active Google Sheet.
 * Deploy as: Deploy > New deployment > Web app > Execute as: Me, Access: Anyone.
 * Then paste the web app URL into FORM_ENDPOINT in web/apply.html.
 */
const HEADERS = ["submitted_at", "name", "phone", "email", "state", "license",
                 "experience", "own_truck", "endorsements", "start", "consent"];

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    if (!data.consent) return out_({ ok: false, error: "consent required" });
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);
    // Prefix with ' so phone numbers are kept as text.
    sheet.appendRow(HEADERS.map(k => k === "phone" ? "'" + (data[k] || "") : (data[k] || "")));
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, error: String(err) });
  }
}

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
