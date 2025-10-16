/**
 * Manual Test Post Creator
 * Creates a test draft post for review testing
 */

const { Client } = require('@notionhq/client');

// Environment variables
const NOTION_API_KEY = process.env.NOTION_API_KEY;
const NOTION_DB_ID = process.env.NOTION_DB_ID;

const notion = new Client({ auth: NOTION_API_KEY });

module.exports = async (req, res) => {
    try {
        console.log('🧪 Creating test draft post...');
        
        // Create a test blog post
        const testPost = {
            title: "AI Headshots: The Future of Professional Photography",
            slug: "ai-headshots-future-professional-photography",
            excerpt: "Discover how AI-powered headshot generation is revolutionizing professional photography and personal branding.",
            content: `# AI Headshots: The Future of Professional Photography

In today's digital-first world, professional headshots are more important than ever. Whether you're updating your LinkedIn profile, creating a company website, or building your personal brand, your headshot is often the first impression people have of you.

## The Traditional Photography Challenge

Traditional professional photography comes with several challenges:
- **High Costs**: Professional photo shoots can cost hundreds or thousands of dollars
- **Time Constraints**: Scheduling sessions around busy work schedules
- **Location Limitations**: Finding the right photographer in your area
- **Weather Dependencies**: Outdoor shoots affected by weather conditions

## Enter AI-Powered Solutions

AI headshot generation technology has emerged as a game-changing solution. Platforms like Brightface.ai are making professional-quality headshots accessible to everyone.

### Key Benefits:
- **Cost-Effective**: Generate multiple professional headshots for a fraction of traditional costs
- **Convenient**: Create headshots from the comfort of your home
- **Consistent Quality**: AI ensures professional lighting and composition every time
- **Multiple Styles**: Choose from various professional styles and backgrounds

## The Technology Behind AI Headshots

Modern AI headshot generators use advanced machine learning models trained on thousands of professional photographs. This allows them to:

1. **Analyze facial features** and maintain authenticity
2. **Apply professional lighting** and composition rules
3. **Generate multiple variations** in different styles
4. **Ensure consistency** across all generated images

## Perfect for Modern Professionals

AI headshots are particularly valuable for:
- **Remote workers** who need professional images for virtual meetings
- **Entrepreneurs** building their personal brand
- **Job seekers** updating their professional profiles
- **Content creators** needing consistent branding

## The Future is Here

As AI technology continues to advance, we can expect even more sophisticated features:
- **Real-time generation** for instant results
- **Custom style training** based on your preferences
- **Integration with professional platforms** for seamless updates

## Getting Started

Ready to transform your professional image? Try AI headshot generation today and experience the future of professional photography.

*This technology is revolutionizing how we approach personal branding and professional presentation in the digital age.*`,
            tags: ["AI", "Professional Photography", "Personal Branding", "Technology"],
            seoTitle: "AI Headshots: The Future of Professional Photography | Brightface",
            seoDescription: "Discover how AI-powered headshot generation is revolutionizing professional photography and personal branding. Learn about the benefits and technology behind AI headshots."
        };

        // Create the post in Notion
        const pageData = {
            parent: { database_id: NOTION_DB_ID },
            properties: {
                Name: { title: [{ text: { content: testPost.title } }] },
                Slug: { rich_text: [{ text: { content: testPost.slug } }] },
                Excerpt: { rich_text: [{ text: { content: testPost.excerpt } }] },
                // Status: { select: { name: 'Draft' } },
                Tags: { multi_select: testPost.tags.map(tag => ({ name: tag })) },
                'SEO Title': { rich_text: [{ text: { content: testPost.seoTitle } }] },
                'SEO Description': { rich_text: [{ text: { content: testPost.seoDescription } }] },
                'Publish Date': { date: { start: new Date().toISOString().split('T')[0] } }
            },
            children: [
                {
                    object: 'block',
                    type: 'heading_1',
                    heading_1: {
                        rich_text: [{ text: { content: 'AI Headshots: The Future of Professional Photography' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [{ text: { content: 'In today\'s digital-first world, professional headshots are more important than ever. Whether you\'re updating your LinkedIn profile, creating a company website, or building your personal brand, your headshot is often the first impression people have of you.' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'heading_2',
                    heading_2: {
                        rich_text: [{ text: { content: 'The Traditional Photography Challenge' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [{ text: { content: 'Traditional professional photography comes with several challenges:' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'High Costs: Professional photo shoots can cost hundreds or thousands of dollars' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Time Constraints: Scheduling sessions around busy work schedules' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Location Limitations: Finding the right photographer in your area' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Weather Dependencies: Outdoor shoots affected by weather conditions' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'heading_2',
                    heading_2: {
                        rich_text: [{ text: { content: 'Enter AI-Powered Solutions' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [{ text: { content: 'AI headshot generation technology has emerged as a game-changing solution. Platforms like Brightface.ai are making professional-quality headshots accessible to everyone.' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'heading_3',
                    heading_3: {
                        rich_text: [{ text: { content: 'Key Benefits:' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Cost-Effective: Generate multiple professional headshots for a fraction of traditional costs' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Convenient: Create headshots from the comfort of your home' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Consistent Quality: AI ensures professional lighting and composition every time' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'bulleted_list_item',
                    bulleted_list_item: {
                        rich_text: [{ text: { content: 'Multiple Styles: Choose from various professional styles and backgrounds' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'heading_2',
                    heading_2: {
                        rich_text: [{ text: { content: 'Perfect for Modern Professionals' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [{ text: { content: 'AI headshots are particularly valuable for remote workers, entrepreneurs, job seekers, and content creators who need consistent professional branding.' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'heading_2',
                    heading_2: {
                        rich_text: [{ text: { content: 'Getting Started' } }]
                    }
                },
                {
                    object: 'block',
                    type: 'paragraph',
                    paragraph: {
                        rich_text: [{ text: { content: 'Ready to transform your professional image? Try AI headshot generation today and experience the future of professional photography.' } }]
                    }
                }
            ]
        };

        const response = await notion.pages.create(pageData);
        
        console.log(`✅ Test draft created: ${response.id}`);
        
        res.status(200).json({
            success: true,
            message: 'Test draft post created successfully',
            postId: response.id,
            title: testPost.title,
            slug: testPost.slug,
            status: 'Draft',
            instructions: 'Check your Notion database for the new draft post. Change status from "Draft" to "Published" to make it live on your blog.'
        });
        
    } catch (error) {
        console.error('❌ Error creating test post:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
};
