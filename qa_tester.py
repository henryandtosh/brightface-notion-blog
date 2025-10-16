"""
Testing and QA Controls for Brightface Content Engine
"""
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import random

from models import RSSItem, ContentItem, ContentStatus, ContentScore, GeneratedContent
from rss_manager import RSSManager
from scoring_ai import ScoringAI
from quality_filter import QualityFilter
from content_ai import ContentAI
from sheets_manager import GoogleSheetsManager
from social_publishers import SocialMediaManager
from config import Config

logger = logging.getLogger(__name__)

class ContentEngineTester:
    """Testing and QA utilities for the content engine"""
    
    def __init__(self):
        self.rss_manager = RSSManager()
        self.scoring_ai = ScoringAI()
        self.quality_filter = QualityFilter()
        self.content_ai = ContentAI()
        self.sheets_manager = GoogleSheetsManager()
        self.social_manager = SocialMediaManager()
    
    def test_rss_feeds(self) -> Dict[str, Any]:
        """Test RSS feed fetching"""
        logger.info("Testing RSS feed fetching...")
        
        results = {
            'feeds_tested': 0,
            'feeds_successful': 0,
            'total_items': 0,
            'errors': []
        }
        
        for feed_url in Config.RSS_SOURCES:
            try:
                items = self.rss_manager._fetch_single_feed(feed_url)
                results['feeds_tested'] += 1
                results['total_items'] += len(items)
                
                if items:
                    results['feeds_successful'] += 1
                    logger.info(f"✓ {feed_url}: {len(items)} items")
                else:
                    logger.warning(f"⚠ {feed_url}: No items found")
                    
            except Exception as e:
                results['errors'].append(f"{feed_url}: {e}")
                logger.error(f"✗ {feed_url}: {e}")
        
        success_rate = (results['feeds_successful'] / results['feeds_tested'] * 100) if results['feeds_tested'] > 0 else 0
        logger.info(f"RSS Test Results: {success_rate:.1f}% success rate, {results['total_items']} total items")
        
        return results
    
    def test_scoring_ai(self, sample_size: int = 5) -> Dict[str, Any]:
        """Test the scoring AI with sample content"""
        logger.info(f"Testing scoring AI with {sample_size} samples...")
        
        results = {
            'samples_tested': 0,
            'samples_successful': 0,
            'avg_relevance': 0,
            'avg_virality': 0,
            'errors': []
        }
        
        # Fetch some RSS items for testing
        rss_items = self.rss_manager.fetch_rss_feeds()
        test_items = rss_items[:sample_size] if len(rss_items) >= sample_size else rss_items
        
        relevance_scores = []
        virality_scores = []
        
        for item in test_items:
            try:
                score = self.scoring_ai.score_content(item)
                results['samples_tested'] += 1
                
                if score:
                    results['samples_successful'] += 1
                    relevance_scores.append(score.relevance_score)
                    virality_scores.append(score.virality_score)
                    logger.info(f"✓ Scored '{item.title}': relevance={score.relevance_score}, virality={score.virality_score}")
                else:
                    logger.warning(f"⚠ Failed to score '{item.title}'")
                    
            except Exception as e:
                results['errors'].append(f"Scoring error for '{item.title}': {e}")
                logger.error(f"✗ Error scoring '{item.title}': {e}")
        
        if relevance_scores:
            results['avg_relevance'] = sum(relevance_scores) / len(relevance_scores)
            results['avg_virality'] = sum(virality_scores) / len(virality_scores)
        
        success_rate = (results['samples_successful'] / results['samples_tested'] * 100) if results['samples_tested'] > 0 else 0
        logger.info(f"Scoring Test Results: {success_rate:.1f}% success rate, avg relevance={results['avg_relevance']:.1f}, avg virality={results['avg_virality']:.1f}")
        
        return results
    
    def test_content_generation(self, sample_size: int = 3) -> Dict[str, Any]:
        """Test content generation with sample scored items"""
        logger.info(f"Testing content generation with {sample_size} samples...")
        
        results = {
            'samples_tested': 0,
            'samples_successful': 0,
            'linkedin_lengths': [],
            'x_lengths': [],
            'blog_lengths': [],
            'errors': []
        }
        
        # Get some scored items
        rss_items = self.rss_manager.fetch_rss_feeds()
        test_items = rss_items[:sample_size] if len(rss_items) >= sample_size else rss_items
        
        for item in test_items:
            try:
                # Score the item first
                score = self.scoring_ai.score_content(item)
                if not score:
                    continue
                
                # Generate content
                generated_content = self.content_ai.generate_content(item, score)
                results['samples_tested'] += 1
                
                if generated_content:
                    results['samples_successful'] += 1
                    
                    # Check lengths
                    linkedin_len = len(generated_content.linkedin.text)
                    x_len = len(generated_content.x.text)
                    blog_len = len(generated_content.blog.body_md)
                    
                    results['linkedin_lengths'].append(linkedin_len)
                    results['x_lengths'].append(x_len)
                    results['blog_lengths'].append(blog_len)
                    
                    logger.info(f"✓ Generated content for '{item.title}': LinkedIn={linkedin_len} chars, X={x_len} chars, Blog={blog_len} chars")
                else:
                    logger.warning(f"⚠ Failed to generate content for '{item.title}'")
                    
            except Exception as e:
                results['errors'].append(f"Generation error for '{item.title}': {e}")
                logger.error(f"✗ Error generating content for '{item.title}': {e}")
        
        success_rate = (results['samples_successful'] / results['samples_tested'] * 100) if results['samples_tested'] > 0 else 0
        logger.info(f"Content Generation Test Results: {success_rate:.1f}% success rate")
        
        return results
    
    def test_quality_filters(self, sample_size: int = 10) -> Dict[str, Any]:
        """Test quality filters with sample content"""
        logger.info(f"Testing quality filters with {sample_size} samples...")
        
        results = {
            'samples_tested': 0,
            'passed_filter': 0,
            'held_for_review': 0,
            'rejected': 0,
            'pass_rate': 0,
            'errors': []
        }
        
        # Get some RSS items and score them
        rss_items = self.rss_manager.fetch_rss_feeds()
        test_items = rss_items[:sample_size] if len(rss_items) >= sample_size else rss_items
        
        for item in test_items:
            try:
                score = self.scoring_ai.score_content(item)
                if not score:
                    continue
                
                results['samples_tested'] += 1
                
                # Test first quality filter
                passed, reason = self.quality_filter.filter_by_score(item, score)
                
                if passed:
                    results['passed_filter'] += 1
                    logger.info(f"✓ Passed filter: '{item.title}'")
                else:
                    # Check if should be held for review
                    should_review, review_reason = self.quality_filter.should_hold_for_review(item, score)
                    if should_review:
                        results['held_for_review'] += 1
                        logger.info(f"⚠ Held for review: '{item.title}' - {review_reason}")
                    else:
                        results['rejected'] += 1
                        logger.info(f"✗ Rejected: '{item.title}' - {reason}")
                        
            except Exception as e:
                results['errors'].append(f"Filter test error for '{item.title}': {e}")
                logger.error(f"✗ Error testing filters for '{item.title}': {e}")
        
        results['pass_rate'] = (results['passed_filter'] / results['samples_tested'] * 100) if results['samples_tested'] > 0 else 0
        logger.info(f"Quality Filter Test Results: {results['pass_rate']:.1f}% pass rate, {results['held_for_review']} held for review, {results['rejected']} rejected")
        
        return results
    
    def test_sheets_integration(self) -> Dict[str, Any]:
        """Test Google Sheets integration"""
        logger.info("Testing Google Sheets integration...")
        
        results = {
            'connection_successful': False,
            'sheet_created': False,
            'data_logged': False,
            'errors': []
        }
        
        try:
            # Test connection
            seen_urls = self.sheets_manager.get_seen_urls()
            results['connection_successful'] = True
            logger.info("✓ Google Sheets connection successful")
            
            # Test sheet creation
            if self.sheets_manager.create_content_ledger():
                results['sheet_created'] = True
                logger.info("✓ Content ledger sheet created/updated")
            
            # Test data logging (with dummy data)
            dummy_item = self._create_dummy_content_item()
            if self.sheets_manager.log_content_item(dummy_item):
                results['data_logged'] = True
                logger.info("✓ Data logging successful")
                
        except Exception as e:
            results['errors'].append(f"Sheets integration error: {e}")
            logger.error(f"✗ Google Sheets integration error: {e}")
        
        return results
    
    def _create_dummy_content_item(self) -> ContentItem:
        """Create a dummy content item for testing"""
        from models import RSSItem, ContentScore, GeneratedContent, SocialPost, BlogDraft, RiskFlag
        
        rss_item = RSSItem(
            title="Test Article",
            summary="This is a test article for QA purposes",
            source="test.com",
            url="https://test.com/article",
            url_hash="test123"
        )
        
        score = ContentScore(
            relevance_score=8,
            virality_score=7,
            freshness_days=1,
            angles=["Test angle"],
            risk_flags=[RiskFlag.NONE],
            one_line_take="Test hook for content",
            keywords=["test", "ai", "headshots"]
        )
        
        generated_content = GeneratedContent(
            linkedin=SocialPost(text="Test LinkedIn post", hashtags=["#test"]),
            x=SocialPost(text="Test X post", hashtags=["#test"]),
            blog=BlogDraft(title="Test Blog", slug="test-blog", meta_description="Test description", outline=["Test outline"], body_md="Test body")
        )
        
        return ContentItem(
            rss_item=rss_item,
            score=score,
            generated_content=generated_content,
            status=ContentStatus.APPROVED
        )
    
    def run_full_qa_test(self) -> Dict[str, Any]:
        """Run a complete QA test suite"""
        logger.info("Running full QA test suite...")
        
        test_results = {
            'start_time': datetime.now(),
            'rss_test': {},
            'scoring_test': {},
            'content_generation_test': {},
            'quality_filter_test': {},
            'sheets_test': {},
            'overall_success': False
        }
        
        try:
            # Run all tests
            test_results['rss_test'] = self.test_rss_feeds()
            test_results['scoring_test'] = self.test_scoring_ai()
            test_results['content_generation_test'] = self.test_content_generation()
            test_results['quality_filter_test'] = self.test_quality_filters()
            test_results['sheets_test'] = self.test_sheets_integration()
            
            # Determine overall success
            all_tests_passed = (
                test_results['rss_test']['feeds_successful'] > 0 and
                test_results['scoring_test']['samples_successful'] > 0 and
                test_results['content_generation_test']['samples_successful'] > 0 and
                test_results['sheets_test']['connection_successful']
            )
            
            test_results['overall_success'] = all_tests_passed
            
        except Exception as e:
            logger.error(f"Error in QA test suite: {e}")
            test_results['error'] = str(e)
        
        test_results['end_time'] = datetime.now()
        test_results['duration'] = (test_results['end_time'] - test_results['start_time']).total_seconds()
        
        # Log results
        if test_results['overall_success']:
            logger.info("✓ All QA tests passed!")
        else:
            logger.warning("⚠ Some QA tests failed - check logs for details")
        
        return test_results
    
    def generate_qa_report(self, test_results: Dict[str, Any]) -> str:
        """Generate a human-readable QA report"""
        report = f"""
# Brightface Content Engine - QA Test Report
Generated: {test_results['end_time'].strftime('%Y-%m-%d %H:%M:%S')}
Duration: {test_results['duration']:.1f} seconds
Overall Status: {'✓ PASSED' if test_results['overall_success'] else '✗ FAILED'}

## Test Results

### RSS Feed Test
- Feeds Tested: {test_results['rss_test']['feeds_tested']}
- Feeds Successful: {test_results['rss_test']['feeds_successful']}
- Total Items: {test_results['rss_test']['total_items']}
- Errors: {len(test_results['rss_test']['errors'])}

### Scoring AI Test
- Samples Tested: {test_results['scoring_test']['samples_tested']}
- Samples Successful: {test_results['scoring_test']['samples_successful']}
- Avg Relevance Score: {test_results['scoring_test']['avg_relevance']:.1f}
- Avg Virality Score: {test_results['scoring_test']['avg_virality']:.1f}

### Content Generation Test
- Samples Tested: {test_results['content_generation_test']['samples_tested']}
- Samples Successful: {test_results['content_generation_test']['samples_successful']}

### Quality Filter Test
- Samples Tested: {test_results['quality_filter_test']['samples_tested']}
- Pass Rate: {test_results['quality_filter_test']['pass_rate']:.1f}%
- Held for Review: {test_results['quality_filter_test']['held_for_review']}
- Rejected: {test_results['quality_filter_test']['rejected']}

### Google Sheets Test
- Connection: {'✓' if test_results['sheets_test']['connection_successful'] else '✗'}
- Sheet Created: {'✓' if test_results['sheets_test']['sheet_created'] else '✗'}
- Data Logged: {'✓' if test_results['sheets_test']['data_logged'] else '✗'}

## Recommendations
"""
        
        if not test_results['overall_success']:
            report += "- Review failed tests and fix issues before production deployment\n"
        
        if test_results['quality_filter_test']['pass_rate'] < 70:
            report += "- Consider adjusting quality filter thresholds (current pass rate < 70%)\n"
        
        if test_results['rss_test']['feeds_successful'] < len(Config.RSS_SOURCES):
            report += "- Some RSS feeds are not working - check feed URLs\n"
        
        report += "- Run tests regularly to ensure system health\n"
        
        return report

def main():
    """Run QA tests"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    tester = ContentEngineTester()
    results = tester.run_full_qa_test()
    
    # Generate and print report
    report = tester.generate_qa_report(results)
    print(report)
    
    # Save report to file
    with open('qa_report.txt', 'w') as f:
        f.write(report)
    
    logger.info("QA report saved to qa_report.txt")

if __name__ == "__main__":
    main()
