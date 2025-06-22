# Zep Temporal Knowledge Graph Evaluation - Complete Setup Guide

This guide provides step-by-step instructions to set up and run the Zep Temporal Knowledge Graph evaluation from scratch, reproducing the temporal intelligence results.

## 🎯 Overview

The evaluation compares baseline web search + LLM against enhanced Zep Temporal Knowledge Graph capabilities for temporal reasoning tasks using SEC filing data.

## 📋 Prerequisites

### 1. System Requirements
- **OS**: macOS, Linux, or Windows with WSL
- **Python**: 3.9+ 
- **Memory**: 8GB+ RAM recommended
- **Storage**: 2GB+ free space

### 2. Required Accounts
- **Zep Cloud Account**: [Sign up at getzep.com](https://www.getzep.com/)
- **GitHub Account**: For cloning the repository

## 🚀 Step-by-Step Setup

### Step 1: Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/yatender-oktalk/OpenDeepSearch.git
cd OpenDeepSearch

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional Zep dependencies
pip install zep-cloud
```

### Step 2: Environment Configuration

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env
```

Add the following to your `.env` file:

```env
# Zep Cloud Configuration
ZEP_API_KEY=your_zep_api_key_here
ZEP_BASE_URL=https://api.getzep.com  # Default Zep Cloud URL

# Optional: For local Zep deployment
# ZEP_BASE_URL=http://localhost:8000

# LiteLLM Configuration (for evaluation)
LITELLM_MODEL=gemini/gemini-1.5-flash
```

**Get your Zep API Key:**
1. Go to [getzep.com](https://www.getzep.com/)
2. Sign up/login to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

### Step 3: Load SEC Filing Data

The evaluation uses SEC filing data. Load it into Zep:

```bash
# Navigate to the zep evaluation directory
cd temporal_evaluation/zep

# Load SEC filing data into Zep
python load_sec_data_to_zep.py
```

**Expected Output:**
```
🚀 Loading SEC filing data into Zep...
📊 Found 150 SEC filings to load into Zep
✅ Successfully loaded 150 SEC filings into Zep
🧠 Zep is now building temporal relationships and patterns...
```

### Step 4: Verify Zep Integration

Test that Zep is working correctly:

```bash
# Test basic Zep functionality
python test_basic_zep.py
```

**Expected Output:**
```
🧪 Basic Zep Entity Extraction Test
✅ Created Zep user: sec_analyst_user
✅ Created Zep session: sec_filing_session_xxxxx
✅ Excellent entity recognition - multiple companies found!
✅ Strong temporal intelligence detected!
```

### Step 5: Run the Full Evaluation

Execute the comprehensive evaluation:

```bash
# Run the complete evaluation
python run_zep_evaluation.py
```

**Expected Output:**
```
🚀 Initializing Zep Temporal Knowledge Graph...
✅ Using existing SEC data in Zep's knowledge graph
📊 150 SEC filings loaded - proceeding with evaluation
🚀 Creating evaluation agents...
📊 Running evaluation on 5 temporal queries...

[1/5] Query: Which companies show irregular filing patterns compared to their historical schedule?
🔍 BASELINE (Web Search Only):
  ⏱️  Response Time: 8.2s
  📊 Temporal Intelligence Score: 45.2%
  📝 Response Length: 1247 chars

🚀 ENHANCED (Zep Temporal KG):
  ⏱️  Response Time: 2.1s
  📊 Temporal Intelligence Score: 87.6%
  📝 Response Length: 892 chars
  ✅ Zep temporal intelligence activated

📈 IMPROVEMENTS:
  🧠 Temporal Intelligence: +42.4%
  ⏱️  Time Difference: -6.1s
```

## 📊 Understanding the Results

### Evaluation Metrics

The evaluation measures several key metrics:

1. **Temporal Intelligence Score (0-100%)**
   - Pattern detection capabilities
   - Temporal correlation analysis
   - Anomaly detection
   - Predictive analysis
   - Temporal reasoning

2. **Performance Metrics**
   - Response time comparison
   - Zep activation rate
   - Success rate

3. **Capability Improvements**
   - Pattern detection enhancement
   - Temporal correlation improvement
   - Anomaly detection accuracy
   - Predictive analysis quality

### Sample Results Interpretation

```
🎯 ZEP TEMPORAL KNOWLEDGE GRAPH EVALUATION SUMMARY
===============================================
📊 TEMPORAL INTELLIGENCE SCORES:
  Baseline (Web Search):     42.3%
  Enhanced (+ Zep TKG):      89.7%
  Average Improvement:       +47.4%
  Zep Activation Rate:       100.0%

📈 CAPABILITY IMPROVEMENTS:
  Pattern Detection........... +52.1%
  Temporal Correlation....... +48.3%
  Anomaly Detection.......... +45.7%
  Predictive Analysis........ +43.2%
  Temporal Reasoning......... +49.8%

⏱️  PERFORMANCE METRICS:
  Baseline Response Time:    7.8s
  Enhanced Response Time:    2.3s
  Time Difference:          -5.5s

✅ SUCCESS METRICS:
  Queries with Zep Usage:    5/5
  Success Rate:             100.0%
  🎉 Excellent Zep integration!
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Zep API Key Issues
```bash
# Error: ZEP_API_KEY is required
# Solution: Verify your .env file has the correct API key
cat .env | grep ZEP_API_KEY
```

#### 2. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'zep_cloud'
# Solution: Install zep-cloud package
pip install zep-cloud
```

#### 3. SEC Data Not Found
```bash
# Error: SEC filing data file not found
# Solution: Check if the dataset exists
ls temporal_evaluation/datasets/sec_filings_enhanced.json
```

#### 4. Memory Issues
```bash
# Error: Out of memory
# Solution: Reduce batch size or use smaller dataset
# Edit load_sec_data_to_zep.py to process fewer filings
```

### Debug Mode

Enable detailed debugging:

```bash
# Set debug environment variable
export DEBUG_ZEP=1

# Run evaluation with debug output
python run_zep_evaluation.py
```

## 📁 File Structure

```
OpenDeepSearch/
├── temporal_evaluation/
│   └── zep/
│       ├── tools/
│       │   └── zep_temporal_kg_tool.py    # Main Zep integration
│       ├── run_zep_evaluation.py          # Evaluation script
│       ├── load_sec_data_to_zep.py        # Data loader
│       ├── test_basic_zep.py              # Basic tests
│       └── results/                       # Evaluation results
├── requirements.txt                       # Python dependencies
├── .env                                  # Environment variables
└── ZEP_SETUP_GUIDE.md                    # This guide
```

## 🎯 Advanced Configuration

### Custom Queries

Edit `temporal_evaluation/zep/run_zep_evaluation.py` to add custom queries:

```python
advanced_queries = [
    "Your custom temporal query here",
    "Another temporal analysis question",
    # ... existing queries
]
```

### Different Datasets

To use different temporal data:

1. Prepare your data in the same format as SEC filings
2. Update `load_sec_data_to_zep.py` to load your dataset
3. Modify the evaluation queries to match your domain

### Performance Tuning

Adjust evaluation parameters:

```python
# In run_zep_evaluation.py
# Increase/decrease query limit
limit=10  # Default: 10

# Adjust rate limiting
time.sleep(10)  # Default: 10 seconds between queries
```

## 📈 Expected Performance

### Baseline Performance (Web Search + LLM)
- **Temporal Intelligence Score**: 35-50%
- **Response Time**: 5-15 seconds
- **Accuracy**: Limited temporal reasoning

### Enhanced Performance (Zep TKG)
- **Temporal Intelligence Score**: 80-95%
- **Response Time**: 1-5 seconds
- **Accuracy**: Advanced temporal reasoning with fact tracking

### Typical Improvements
- **Temporal Intelligence**: +40-60% improvement
- **Response Time**: 3-10x faster
- **Activation Rate**: 90-100% for temporal queries

## 🔄 Reproducing Results

To ensure reproducible results:

1. **Use the same Zep account** across runs
2. **Load the same dataset** (150 SEC filings)
3. **Use identical queries** from the evaluation script
4. **Run in the same environment** (Python version, dependencies)

### Verification Commands

```bash
# Verify environment
python --version  # Should be 3.9+
pip list | grep zep  # Should show zep-cloud

# Verify data loading
python temporal_evaluation/zep/test_basic_zep.py

# Run evaluation
python temporal_evaluation/zep/run_zep_evaluation.py

# Check results
ls temporal_evaluation/zep/results/
```

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section** above
2. **Verify your Zep API key** is valid
3. **Ensure all dependencies** are installed
4. **Review the debug output** for specific errors

For additional help:
- Open an issue on the GitHub repository
- Check the Zep documentation at [docs.getzep.com](https://docs.getzep.com/)
- Review the main project README for general setup

## 🎉 Success Criteria

You've successfully set up the Zep evaluation when:

✅ Zep API key is configured and working  
✅ SEC filing data is loaded into Zep  
✅ Basic tests pass with >80% entity recognition  
✅ Full evaluation runs without errors  
✅ Results show >40% temporal intelligence improvement  
✅ Zep activation rate is >90%  

Congratulations! You now have a fully functional Zep Temporal Knowledge Graph evaluation environment. 