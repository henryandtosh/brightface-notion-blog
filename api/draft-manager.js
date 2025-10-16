/**
 * Draft Management API
 * Allows reviewing and approving draft posts
 */

const { Client } = require('@notionhq/client');

// Environment variables
const NOTION_API_KEY = process.env.NOTION_API_KEY;
const NOTION_DB_ID = process.env.NOTION_DB_ID;

const notion = new Client({ auth: NOTION_API_KEY });

module.exports = async (req, res) => {
    try {
        const { method } = req;
        
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
        
        if (method === 'OPTIONS') {
            res.status(200).end();
            return;
        }
        
        if (method === 'GET') {
            // Get all drafts
            const drafts = await getDrafts();
            res.status(200).json({
                success: true,
                data: drafts
            });
        } else if (method === 'POST') {
            const { action, postId } = req.body;
            
            if (action === 'approve') {
                // Approve a draft (change status to Published)
                await approveDraft(postId);
                res.status(200).json({
                    success: true,
                    message: 'Draft approved and published'
                });
            } else if (action === 'reject') {
                // Reject a draft (change status to Rejected)
                await rejectDraft(postId);
                res.status(200).json({
                    success: true,
                    message: 'Draft rejected'
                });
            } else {
                res.status(400).json({
                    success: false,
                    error: 'Invalid action'
                });
            }
        } else {
            res.status(405).json({
                success: false,
                error: 'Method not allowed'
            });
        }
        
    } catch (error) {
        console.error('Error in draft management:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
};

async function getDrafts() {
    try {
        const response = await notion.databases.query({
            database_id: NOTION_DB_ID,
            filter: {
                property: 'Status',
                select: {
                    equals: 'Draft'
                }
            },
            sorts: [
                {
                    property: 'Created',
                    direction: 'descending'
                }
            ]
        });

        return response.results.map(post => ({
            id: post.id,
            title: getPropertyValue(post.properties.Name, 'title'),
            slug: getPropertyValue(post.properties.Slug, 'rich_text'),
            excerpt: getPropertyValue(post.properties.Excerpt, 'rich_text'),
            tags: getPropertyValue(post.properties.Tags, 'multi_select'),
            createdAt: post.created_time,
            updatedAt: post.last_edited_time,
            url: `https://blog.brightface.ai/post?slug=${getPropertyValue(post.properties.Slug, 'rich_text')}`
        }));
    } catch (error) {
        console.error('Error fetching drafts:', error);
        return [];
    }
}

async function approveDraft(postId) {
    try {
        await notion.pages.update({
            page_id: postId,
            properties: {
                Status: { select: { name: 'Published' } },
                'Publish Date': { date: { start: new Date().toISOString().split('T')[0] } }
            }
        });
    } catch (error) {
        console.error('Error approving draft:', error);
        throw error;
    }
}

async function rejectDraft(postId) {
    try {
        await notion.pages.update({
            page_id: postId,
            properties: {
                Status: { select: { name: 'Rejected' } }
            }
        });
    } catch (error) {
        console.error('Error rejecting draft:', error);
        throw error;
    }
}

function getPropertyValue(property, type) {
    if (!property || !property[type]) return null;
    
    switch (type) {
        case 'title':
            return property.title.map(text => text.plain_text).join('');
        case 'rich_text':
            return property.rich_text.map(text => text.plain_text).join('');
        case 'multi_select':
            return property.multi_select.map(option => option.name);
        case 'date':
            return property.date?.start || null;
        case 'people':
            return property.people.map(person => ({
                name: person.name,
                avatar_url: person.avatar_url
            }));
        case 'files':
            return property.files.map(file => ({
                name: file.name,
                url: file.file?.url || file.external?.url
            }));
        default:
            return null;
    }
}
