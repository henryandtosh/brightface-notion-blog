const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
    try {
        const blogHtmlPath = path.join(__dirname, '..', 'blog.html');
        const htmlTemplate = fs.readFileSync(blogHtmlPath, 'utf8');
        
        // Fetch posts data
        const apiResponse = await fetch('https://contentengine-blond.vercel.app/api/blog/posts');
        const data = await apiResponse.json();
        
        if (!data.success) {
            res.status(500).send('Error loading posts');
            return;
        }
        
        // Replace the JavaScript template with actual data
        const postsHtml = data.data.map(post => `
            <article class="post">
                <h2 class="post-title">${escapeHtml(post.title)}</h2>
                
                <div class="post-meta">
                    <span>📅 ${formatDate(post.publishDate || post.createdAt)}</span>
                    ${post.author ? `<span>👤 ${escapeHtml(post.author)}</span>` : ''}
                </div>
                
                ${post.excerpt ? `<div class="post-excerpt">${escapeHtml(post.excerpt)}</div>` : ''}
                
                ${post.tags && post.tags.length > 0 ? `
                    <div class="post-tags">
                        ${post.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
                
                <a href="/post?slug=${post.slug}" class="read-more">
                    Read More →
                </a>
            </article>
        `).join('');
        
        // Replace the posts container with actual data
        const finalHtml = htmlTemplate
            .replace('<div id="posts-container"></div>', `<div id="posts-container">${postsHtml}</div>`)
            .replace('document.addEventListener(\'DOMContentLoaded\', loadPosts);', '// Posts loaded server-side');
        
        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(finalHtml);
        
    } catch (error) {
        console.error('Error loading blog:', error);
        res.status(500).send('Error loading blog page');
    }
};

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatDate(dateString) {
    if (!dateString) return 'No date';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}
