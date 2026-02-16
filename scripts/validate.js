#!/usr/bin/env node
/**
 * Meta Agent Test Runner
 * 
 * Validates the structure and content of all created files.
 * Run with: node scripts/validate.js
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');

// Files that should exist
const REQUIRED_FILES = [
  // Core modules
  'metagpt/core/__init__.py',
  'metagpt/core/heart.py',
  'metagpt/core/soul.py',
  'metagpt/core/memory.py',
  
  // Meta Agent
  'metagpt/roles/meta_agent.py',
  
  // Utils
  'metagpt/utils/canonical_order.py',
  'metagpt/utils/beads_integration.py',
  
  // Connection Window
  'connection-window/server/main.py',
  'connection-window/src/App.tsx',
  'connection-window/src/App.css',
  'connection-window/src/index.tsx',
  'connection-window/package.json',
  
  // Tests
  'tests/test_core_modules.py',
  
  // Deployment
  'Dockerfile.meta',
  'docker-compose.meta.yml',
  'scripts/deploy.py',
  
  // Documentation
  'plans/implementation-plan.md',
  
  // Config
  '.env',
  '.gitignore',
];

// Check patterns for each file type
const CONTENT_CHECKS = {
  'metagpt/core/heart.py': {
    mustContain: ['class Heart', 'CoreValue', 'LOYALTY', 'HONOR', 'TRUTH', 'RESPECT', 'check_values_alignment'],
  },
  'metagpt/core/soul.py': {
    mustContain: ['class Soul', 'BehaviorMode', 'DecisionType', 'BehaviorPattern', 'DecisionFramework'],
  },
  'metagpt/core/memory.py': {
    mustContain: ['class PersistentMemory', 'MemoryType', 'store', 'recall', 'search'],
  },
  'metagpt/roles/meta_agent.py': {
    mustContain: ['class MetaAgent', 'Heart', 'Soul', 'Memory', 'CanonicalOrder', 'publish_team_message'],
  },
  'metagpt/utils/canonical_order.py': {
    mustContain: ['class CanonicalOrder', 'CanonicalOrderEntry', 'create_order', 'get_session_summary'],
  },
  'connection-window/server/main.py': {
    mustContain: ['FastAPI', 'WebSocket', 'CanonicalOrder', 'broadcast_order'],
  },
  'connection-window/src/App.tsx': {
    mustContain: ['CanonicalOrder', 'AgentStatus', 'WebSocket', 'SessionSummary'],
  },
  'tests/test_core_modules.py': {
    mustContain: ['TestHeart', 'TestSoul', 'TestPersistentMemory', 'TestCanonicalOrder', 'TestIntegration'],
  },
};

let passed = 0;
let failed = 0;

console.log('🔍 Meta Agent Validation\n');
console.log('=' .repeat(50));

// Check required files
console.log('\n📁 Checking required files...\n');

for (const file of REQUIRED_FILES) {
  const filePath = path.join(ROOT_DIR, file);
  
  if (fs.existsSync(filePath)) {
    console.log(`  ✅ ${file}`);
    passed++;
    
    // Check content if defined
    if (CONTENT_CHECKS[file]) {
      const content = fs.readFileSync(filePath, 'utf-8');
      const checks = CONTENT_CHECKS[file];
      
      for (const pattern of checks.mustContain) {
        if (!content.includes(pattern)) {
          console.log(`     ⚠️  Missing pattern: ${pattern}`);
          failed++;
        }
      }
    }
  } else {
    console.log(`  ❌ ${file} - NOT FOUND`);
    failed++;
  }
}

// Check .gitignore contains .env
console.log('\n🔐 Checking security...\n');

const gitignorePath = path.join(ROOT_DIR, '.gitignore');
if (fs.existsSync(gitignorePath)) {
  const gitignore = fs.readFileSync(gitignorePath, 'utf-8');
  if (gitignore.includes('.env')) {
    console.log('  ✅ .env is in .gitignore');
    passed++;
  } else {
    console.log('  ❌ .env is NOT in .gitignore - SECURITY RISK!');
    failed++;
  }
} else {
  console.log('  ❌ .gitignore not found');
  failed++;
}

// Check .env exists but is gitignored
const envPath = path.join(ROOT_DIR, '.env');
if (fs.existsSync(envPath)) {
  console.log('  ✅ .env file exists');
  passed++;
  
  // Verify it's not tracked by git
  try {
    const result = require('child_process').execSync(
      'git ls-files .env',
      { cwd: ROOT_DIR, encoding: 'utf-8' }
    ).trim();
    
    if (result === '') {
      console.log('  ✅ .env is not tracked by git');
      passed++;
    } else {
      console.log('  ❌ .env IS TRACKED BY GIT - SECURITY RISK!');
      failed++;
    }
  } catch (e) {
    console.log('  ⚠️  Could not check git tracking');
  }
}

// Summary
console.log('\n' + '=' .repeat(50));
console.log('\n📊 Summary\n');
console.log(`  ✅ Passed: ${passed}`);
console.log(`  ❌ Failed: ${failed}`);
console.log('\n' + '=' .repeat(50));

if (failed > 0) {
  console.log('\n❌ Validation FAILED\n');
  process.exit(1);
} else {
  console.log('\n✅ Validation PASSED\n');
  process.exit(0);
}
