const fs = require('fs');
const path = require('path');

module.exports = (req, res) => {
    const blogHtmlPath = path.join(__dirname, '..', 'blog.html');
    
    fs.readFile(blogHtmlPath, 'utf8', (err, data) => {
        if (err) {
            res.status(500).send('Error loading blog page');
            return;
        }
        
        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(data);
    });
};
