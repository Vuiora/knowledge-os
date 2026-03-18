#!/usr/bin/env python3
"""
Finance Knowledge System - MVP Validation Script
Validates the first three stages (01-financial-cognition, 02-economic-foundation, 03-company-analysis)
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict

# Base path for the finance knowledge system
BASE_PATH = Path("knowledge/05-insights/finance")

# Expected stages for MVP
MVP_STAGES = [
    "01-financial-cognition",
    "02-economic-foundation", 
    "03-company-analysis"
]

# Required metadata fields
REQUIRED_METADATA_FIELDS = [
    "title", "description", "domain", "module", "content_type",
    "skill_level", "tags", "estimated_time", "difficulty_score",
    "author", "created_at", "updated_at", "version", "language", "status"
]

# Valid values for certain fields
VALID_SKILL_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_CONTENT_TYPES = ["article", "tutorial", "reference", "case-study"]
VALID_STATUSES = ["draft", "published"]

class ValidationReport:
    """Stores validation results"""
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        self.stats = defaultdict(int)
        
    def add_error(self, message: str):
        self.errors.append(f"❌ ERROR: {message}")
        
    def add_warning(self, message: str):
        self.warnings.append(f"⚠️  WARNING: {message}")
        
    def add_info(self, message: str):
        self.info.append(f"ℹ️  INFO: {message}")
        
    def print_report(self):
        """Print the validation report"""
        print("\n" + "="*80)
        print("FINANCE KNOWLEDGE SYSTEM - MVP VALIDATION REPORT")
        print("="*80 + "\n")
        
        # Statistics
        print("📊 STATISTICS:")
        print("-" * 80)
        for key, value in sorted(self.stats.items()):
            print(f"  {key}: {value}")
        print()
        
        # Errors
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            print("-" * 80)
            for error in self.errors:
                print(f"  {error}")
            print()
        else:
            print("✅ NO ERRORS FOUND\n")
            
        # Warnings
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            print("-" * 80)
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        else:
            print("✅ NO WARNINGS\n")
            
        # Info
        if self.info:
            print(f"ℹ️  INFORMATION ({len(self.info)}):")
            print("-" * 80)
            for info in self.info:
                print(f"  {info}")
            print()
            
        # Summary
        print("="*80)
        if not self.errors:
            print("✅ VALIDATION PASSED - MVP Core is ready!")
        else:
            print(f"❌ VALIDATION FAILED - {len(self.errors)} errors found")
        print("="*80 + "\n")


def extract_frontmatter(file_path: Path) -> Tuple[Dict, str]:
    """Extract YAML frontmatter and content from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for frontmatter
        if not content.startswith('---'):
            return {}, content
            
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
            
        try:
            metadata = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return metadata or {}, body
        except yaml.YAMLError as e:
            return {}, content
            
    except Exception as e:
        return {}, ""


def validate_directory_structure(report: ValidationReport):
    """Property 1: Directory Structure Consistency"""
    print("🔍 Validating directory structure...")
    
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        
        # Check if stage directory exists
        if not stage_path.exists():
            report.add_error(f"Stage directory missing: {stage}")
            continue
            
        report.stats[f"Stages found"] += 1
        
        # Check kebab-case naming
        if not re.match(r'^[0-9]{2}-[a-z]+(-[a-z]+)*$', stage):
            report.add_error(f"Directory not in kebab-case: {stage}")
            
        # Check for index.md
        index_file = stage_path / "index.md"
        if not index_file.exists():
            report.add_error(f"Missing index.md in {stage}")
        else:
            report.stats["Index files found"] += 1


def validate_index_files(report: ValidationReport):
    """Property 2: Index File Completeness"""
    print("🔍 Validating index files...")
    
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
            
        index_file = stage_path / "index.md"
        if not index_file.exists():
            continue
            
        metadata, content = extract_frontmatter(index_file)
        
        # Check for navigation links
        if not content or len(content) < 100:
            report.add_warning(f"Index file seems empty or too short: {index_file.relative_to(BASE_PATH)}")
            
        # Check for learning time mention
        if "时间" not in content and "time" not in content.lower():
            report.add_warning(f"No learning time estimate in: {index_file.relative_to(BASE_PATH)}")
            
        # Check for links to subdirectories
        subdirs = [d for d in stage_path.iterdir() if d.is_dir()]
        for subdir in subdirs:
            subdir_name = subdir.name
            if subdir_name not in content:
                report.add_warning(f"Index {index_file.relative_to(BASE_PATH)} missing link to subdirectory: {subdir_name}")


def validate_metadata(report: ValidationReport):
    """Property 3: Metadata Schema Compliance"""
    print("🔍 Validating metadata...")
    
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
            
        # Find all markdown files (excluding index.md at stage level)
        md_files = list(stage_path.rglob("*.md"))
        
        for md_file in md_files:
            if md_file.name == "index.md" and md_file.parent == stage_path:
                continue  # Skip stage-level index files for metadata check
                
            report.stats["Content files checked"] += 1
            
            metadata, content = extract_frontmatter(md_file)
            
            if not metadata:
                report.add_error(f"No metadata found in: {md_file.relative_to(BASE_PATH)}")
                continue
                
            # Check required fields
            missing_fields = []
            for field in REQUIRED_METADATA_FIELDS:
                if field not in metadata:
                    missing_fields.append(field)
                    
            if missing_fields:
                report.add_error(f"Missing metadata fields in {md_file.relative_to(BASE_PATH)}: {', '.join(missing_fields)}")
                
            # Validate field values
            if "skill_level" in metadata and metadata["skill_level"] not in VALID_SKILL_LEVELS:
                report.add_error(f"Invalid skill_level in {md_file.relative_to(BASE_PATH)}: {metadata['skill_level']}")
                
            if "content_type" in metadata and metadata["content_type"] not in VALID_CONTENT_TYPES:
                report.add_error(f"Invalid content_type in {md_file.relative_to(BASE_PATH)}: {metadata['content_type']}")
                
            if "status" in metadata and metadata["status"] not in VALID_STATUSES:
                report.add_error(f"Invalid status in {md_file.relative_to(BASE_PATH)}: {metadata['status']}")
                
            # Check tags
            if "tags" in metadata:
                if not isinstance(metadata["tags"], list):
                    report.add_error(f"Tags should be a list in {md_file.relative_to(BASE_PATH)}")
                elif len(metadata["tags"]) == 0:
                    report.add_warning(f"No tags specified in {md_file.relative_to(BASE_PATH)}")
                    
            # Track statistics
            if "skill_level" in metadata:
                report.stats[f"Files - {metadata['skill_level']}"] += 1
            if "status" in metadata and metadata["status"] == "published":
                report.stats["Published files"] += 1


def validate_content_structure(report: ValidationReport):
    """Property 5: Content Structure Requirements"""
    print("🔍 Validating content structure...")
    
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
            
        md_files = list(stage_path.rglob("*.md"))
        
        for md_file in md_files:
            if md_file.name == "index.md":
                continue
                
            metadata, content = extract_frontmatter(md_file)
            
            if not content or len(content) < 500:
                report.add_warning(f"Content seems too short in: {md_file.relative_to(BASE_PATH)}")
                continue
                
            # Check for required sections
            has_overview = bool(re.search(r'##\s*(概述|Overview)', content, re.IGNORECASE))
            has_examples = bool(re.search(r'##\s*(案例|实践|Example|Case)', content, re.IGNORECASE))
            has_references = bool(re.search(r'##\s*(参考|Reference)', content, re.IGNORECASE))
            
            if not has_overview:
                report.add_warning(f"Missing overview section in: {md_file.relative_to(BASE_PATH)}")
            if not has_examples:
                report.add_warning(f"Missing examples/cases section in: {md_file.relative_to(BASE_PATH)}")
            if not has_references:
                report.add_warning(f"Missing references section in: {md_file.relative_to(BASE_PATH)}")
                
            # Check for Mermaid diagrams
            has_mermaid = "```mermaid" in content
            if not has_mermaid:
                report.add_info(f"No Mermaid diagram found in: {md_file.relative_to(BASE_PATH)}")
                
            # Count word length (approximate)
            word_count = len(content)
            report.stats["Total content characters"] += word_count
            
            if word_count < 2000:
                report.add_warning(f"Content may be too short ({word_count} chars) in: {md_file.relative_to(BASE_PATH)}")


def validate_links(report: ValidationReport):
    """Property 7: Internal Link Validity"""
    print("🔍 Validating internal links...")
    
    all_files = set()
    broken_links = []
    
    # Collect all markdown files
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
        md_files = list(stage_path.rglob("*.md"))
        for md_file in md_files:
            all_files.add(md_file)
            
    # Check links in each file
    for md_file in all_files:
        _, content = extract_frontmatter(md_file)
        
        # Find markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for link_text, link_url in links:
            # Skip external links
            if link_url.startswith('http://') or link_url.startswith('https://'):
                continue
            if link_url.startswith('#'):  # Skip anchor links
                continue
                
            # Resolve relative link
            if link_url.startswith('/'):
                target_path = Path(link_url.lstrip('/'))
            else:
                target_path = (md_file.parent / link_url).resolve()
                
            # Check if target exists
            if not target_path.exists():
                broken_links.append((md_file.relative_to(BASE_PATH), link_url))
                
    if broken_links:
        for source, target in broken_links[:10]:  # Show first 10
            report.add_error(f"Broken link in {source}: {target}")
        if len(broken_links) > 10:
            report.add_error(f"... and {len(broken_links) - 10} more broken links")
    
    report.stats["Internal links checked"] += len([l for f in all_files for l in re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', extract_frontmatter(f)[1]) if not l[1].startswith('http')])


def check_learning_path_coherence(report: ValidationReport):
    """Check if learning path is coherent"""
    print("🔍 Checking learning path coherence...")
    
    # Check if stages are in order
    for i, stage in enumerate(MVP_STAGES):
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
            
        index_file = stage_path / "index.md"
        if not index_file.exists():
            continue
            
        metadata, content = extract_frontmatter(index_file)
        
        # Check for prerequisites mention
        if i > 0:
            prev_stage = MVP_STAGES[i-1]
            if prev_stage not in content and "前置" not in content and "prerequisite" not in content.lower():
                report.add_info(f"Stage {stage} index doesn't mention prerequisites")
                
        # Check for next steps
        if i < len(MVP_STAGES) - 1:
            next_stage = MVP_STAGES[i+1]
            if "下一步" not in content and "next" not in content.lower():
                report.add_info(f"Stage {stage} index doesn't mention next steps")


def check_content_depth(report: ValidationReport):
    """Check content depth and breadth"""
    print("🔍 Checking content depth and breadth...")
    
    stage_file_counts = {}
    
    for stage in MVP_STAGES:
        stage_path = BASE_PATH / stage
        if not stage_path.exists():
            continue
            
        md_files = [f for f in stage_path.rglob("*.md") if f.name != "index.md" or f.parent != stage_path]
        stage_file_counts[stage] = len(md_files)
        
    # Expected minimum files per stage (from design)
    expected_minimums = {
        "01-financial-cognition": 5,
        "02-economic-foundation": 25,
        "03-company-analysis": 40
    }
    
    for stage, expected in expected_minimums.items():
        actual = stage_file_counts.get(stage, 0)
        report.stats[f"Files in {stage}"] = actual
        
        if actual < expected:
            report.add_warning(f"Stage {stage} has {actual} files, expected at least {expected}")
        else:
            report.add_info(f"Stage {stage} has sufficient content ({actual} files)")


def main():
    """Main validation function"""
    report = ValidationReport()
    
    print("\n" + "="*80)
    print("FINANCE KNOWLEDGE SYSTEM - MVP CHECKPOINT VALIDATION")
    print("Validating Stages 1-3: Financial Cognition, Economic Foundation, Company Analysis")
    print("="*80 + "\n")
    
    # Check if base path exists
    if not BASE_PATH.exists():
        report.add_error(f"Base path does not exist: {BASE_PATH}")
        report.print_report()
        return 1
        
    # Run all validations
    validate_directory_structure(report)
    validate_index_files(report)
    validate_metadata(report)
    validate_content_structure(report)
    validate_links(report)
    check_learning_path_coherence(report)
    check_content_depth(report)
    
    # Print report
    report.print_report()
    
    # Return exit code
    return 0 if not report.errors else 1


if __name__ == "__main__":
    exit(main())
