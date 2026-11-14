const downloadReport = async () => {
    if (!result) return;
    try {
const response = await fetch("http://127.0.0.1:8000/api/generate-pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          sender: emailInput.sender,
          recipient: emailInput.recipient,
          subject: emailInput.subject,
          analysis: result
        })
      });
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ISO27037-Report-${result.blockchain_audit.sha256_hash.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF generation failed:", err);
      alert("Could not generate PDF report from backend.");
    }
  };