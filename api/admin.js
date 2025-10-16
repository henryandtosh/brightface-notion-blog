const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
    try {
        const adminHtmlPath = path.join(__dirname, '..', 'admin.html');
        const htmlContent = fs.readFileSync(adminHtmlPath, 'utf8');
        
        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(htmlContent);
        
    } catch (error) {
        console.error('Error loading admin interface:', error);
        res.status(500).send('Error loading admin interface');
    }
};
