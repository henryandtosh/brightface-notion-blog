const fs = require('fs');
const path = require('path');

module.exports = async (req, res) => {
    const slug = req.query.slug || req.url.split('/').pop();
    
    if (!slug) {
        res.status(400).send('Slug parameter required');
        return;
    }
    
    try {
        // Fetch the post data from our API
        const apiResponse = await fetch(`https://contentengine-blond.vercel.app/api/blog/posts/${slug}`);
        const data = await apiResponse.json();
        
        if (!data.success) {
            res.status(404).send(`
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Post Not Found - Brightface Blog</title>
                    <style>
                        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; text-align: center; padding: 2rem; }
                        .error { color: #dc2626; font-size: 1.5rem; margin-bottom: 1rem; }
                        .back-link { color: #2563eb; text-decoration: none; }
                    </style>
                </head>
                <body>
                    <div class="error">Post not found</div>
                    <a href="/blog" class="back-link">← Back to Blog</a>
                </body>
                </html>
            `);
            return;
        }
        
        const post = data.data;
        
        // Generate HTML for the individual post
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(post.title)} - Brightface Blog</title>
    <meta name="description" content="${escapeHtml(post.excerpt || post.title)}">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 1rem 0;
        }
        
        .back-link {
            display: inline-block;
            color: #2563eb;
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 500;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .post {
            background: white;
            border-radius: 12px;
            padding: 3rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .post-title {
            font-size: 2.5rem;
            color: #1f2937;
            margin-bottom: 1.5rem;
            line-height: 1.2;
        }
        
        .post-meta {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 2rem;
            color: #6b7280;
            font-size: 0.9rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .post-excerpt {
            color: #4b5563;
            font-size: 1.2rem;
            line-height: 1.6;
            margin-bottom: 2rem;
            font-style: italic;
            padding: 1rem;
            background: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        }
        
        .post-content {
            color: #374151;
            font-size: 1.1rem;
            line-height: 1.8;
            margin-bottom: 2rem;
        }
        
        .post-content h1, .post-content h2, .post-content h3 {
            color: #1f2937;
            margin: 2rem 0 1rem 0;
        }
        
        .post-content h1 { font-size: 2rem; }
        .post-content h2 { font-size: 1.5rem; }
        .post-content h3 { font-size: 1.25rem; }
        
        .post-content p {
            margin-bottom: 1rem;
        }
        
        .post-content ul, .post-content ol {
            margin: 1rem 0 1rem 2rem;
        }
        
        .post-content li {
            margin-bottom: 0.5rem;
        }
        
        .post-content blockquote {
            border-left: 4px solid #2563eb;
            padding: 1rem 1.5rem;
            margin: 1.5rem 0;
            background: #f9fafb;
            font-style: italic;
        }
        
        .post-content code {
            background: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9rem;
        }
        
        .post-content pre {
            background: #1f2937;
            color: #f9fafb;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
        }
        
        .post-content pre code {
            background: none;
            padding: 0;
            color: inherit;
        }
        
        .post-tags {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
        }
        
        .tag {
            background: #e5e7eb;
            color: #374151;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
        }
        
        .footer {
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: #6b7280;
            border-top: 1px solid #e5e7eb;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .post {
                padding: 2rem 1.5rem;
            }
            
            .post-title {
                font-size: 2rem;
            }
            
            .post-meta {
                flex-direction: column;
                gap: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/blog" class="back-link">← Back to Blog</a>
        </div>
        
        <article class="post">
            <h1 class="post-title">${escapeHtml(post.title)}</h1>
            
            <div class="post-meta">
                <span>📅 ${formatDate(post.publishDate || post.createdAt)}</span>
                ${post.author ? `<span>👤 ${escapeHtml(post.author)}</span>` : ''}
                <span>🕒 ${formatTime(post.createdAt)}</span>
            </div>
            
            ${post.excerpt ? `<div class="post-excerpt">${escapeHtml(post.excerpt)}</div>` : ''}
            
            <div class="post-content">
                ${formatContent(post.content)}
            </div>
            
            ${post.tags && post.tags.length > 0 ? `
                <div class="post-tags">
                    ${post.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
            ` : ''}
        </article>
        
        <div class="footer">
            <p>Powered by Notion API • Built with ❤️</p>
        </div>
    </div>
</body>
</html>
        `;
        
        res.setHeader('Content-Type', 'text/html');
        res.status(200).send(html);
        
    } catch (error) {
        console.error('Error fetching post:', error);
        res.status(500).send('Error loading post');
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

function formatTime(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatContent(content) {
    if (!content || typeof content !== 'object') {
        return '<p>Content not available</p>';
    }
    
    // If content has a simple text property
    if (content.text) {
        return `<p>${escapeHtml(content.text)}</p>`;
    }
    
    // If content has blocks (Notion page structure)
    if (content.blocks && Array.isArray(content.blocks)) {
        return content.blocks.map(block => {
            return formatNotionBlock(block);
        }).join('');
    }
    
    // If content has children (Notion page children)
    if (content.children && Array.isArray(content.children)) {
        return content.children.map(child => {
            return formatNotionBlock(child);
        }).join('');
    }
    
    // Try to fetch content from Notion API if we have a page ID
    return '<p>Content formatting not available</p>';
}

function formatNotionBlock(block) {
    if (!block || !block.type) {
        return '';
    }
    
    switch (block.type) {
        case 'paragraph':
            const paragraphText = extractRichText(block.paragraph?.rich_text || []);
            return paragraphText ? `<p>${paragraphText}</p>` : '';
            
        case 'heading_1':
            const h1Text = extractRichText(block.heading_1?.rich_text || []);
            return h1Text ? `<h1>${h1Text}</h1>` : '';
            
        case 'heading_2':
            const h2Text = extractRichText(block.heading_2?.rich_text || []);
            return h2Text ? `<h2>${h2Text}</h2>` : '';
            
        case 'heading_3':
            const h3Text = extractRichText(block.heading_3?.rich_text || []);
            return h3Text ? `<h3>${h3Text}</h3>` : '';
            
        case 'bulleted_list_item':
            const bulletText = extractRichText(block.bulleted_list_item?.rich_text || []);
            return bulletText ? `<li>${bulletText}</li>` : '';
            
        case 'numbered_list_item':
            const numberedText = extractRichText(block.numbered_list_item?.rich_text || []);
            return numberedText ? `<li>${numberedText}</li>` : '';
            
        case 'quote':
            const quoteText = extractRichText(block.quote?.rich_text || []);
            return quoteText ? `<blockquote>${quoteText}</blockquote>` : '';
            
        case 'code':
            const codeText = extractRichText(block.code?.rich_text || []);
            return codeText ? `<pre><code>${escapeHtml(codeText)}</code></pre>` : '';
            
        case 'divider':
            return '<hr>';
            
        case 'image':
            const imageUrl = block.image?.file?.url || block.image?.external?.url;
            const imageCaption = extractRichText(block.image?.caption || []);
            if (imageUrl) {
                return `<figure><img src="${imageUrl}" alt="${imageCaption || ''}" style="max-width: 100%; height: auto;"><figcaption>${imageCaption}</figcaption></figure>`;
            }
            return '';
            
        case 'callout':
            const calloutText = extractRichText(block.callout?.rich_text || []);
            const calloutIcon = block.callout?.icon?.emoji || '💡';
            return calloutText ? `<div class="callout"><strong>${calloutIcon}</strong> ${calloutText}</div>` : '';
            
        case 'toggle':
            const toggleText = extractRichText(block.toggle?.rich_text || []);
            return toggleText ? `<details><summary>${toggleText}</summary></details>` : '';
            
        default:
            // Try to extract any rich text from unknown block types
            const richText = extractRichText(block[block.type]?.rich_text || []);
            return richText ? `<p>${richText}</p>` : '';
    }
}

function extractRichText(richTextArray) {
    if (!Array.isArray(richTextArray)) {
        return '';
    }
    
    return richTextArray.map(textObj => {
        if (textObj.type === 'text') {
            let content = escapeHtml(textObj.text?.content || '');
            
            // Apply formatting
            if (textObj.annotations) {
                const annotations = textObj.annotations;
                
                if (annotations.bold) content = `<strong>${content}</strong>`;
                if (annotations.italic) content = `<em>${content}</em>`;
                if (annotations.strikethrough) content = `<del>${content}</del>`;
                if (annotations.underline) content = `<u>${content}</u>`;
                if (annotations.code) content = `<code>${content}</code>`;
                
                // Handle links
                if (textObj.text?.link?.url) {
                    content = `<a href="${textObj.text.link.url}" target="_blank" rel="noopener">${content}</a>`;
                }
            }
            
            return content;
        }
        return '';
    }).join('');
}
