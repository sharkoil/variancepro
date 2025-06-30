# VariancePro Troubleshooting Guide

## Common Issues and Solutions

### 1. Timeout Errors with Phi4

**Error**: `Read timed out. (read timeout=60)`

**Causes & Solutions**:

#### First-time Model Loading
- **Issue**: Phi4 takes time to load initially (especially on first use)
- **Solution**: Wait 1-2 minutes for the model to fully load, then try again
- **Check**: Run `ollama ps` to see if the model is loading

#### Complex Queries
- **Issue**: Model takes longer for complex financial analysis
- **Solution**: 
  - Try simpler questions first
  - Break complex questions into smaller parts
  - The app now has 90-second timeout (optimized for Phi4)

#### Insufficient Resources
- **Issue**: System doesn't have enough RAM/CPU for Phi4
- **Solutions**:
  - Close other applications to free up memory
  - Upgrade system RAM (Phi4 needs ~4GB RAM minimum)

### 2. Connection Errors

**Error**: `Cannot connect to Ollama`

**Solutions**:
1. **Start Ollama**: `ollama serve`
2. **Check if running**: `ollama ps`
3. **Restart Ollama**: 
   ```bash
   # Stop
   taskkill /F /IM ollama.exe
   # Start
   ollama serve
   ```

### 3. Model Not Found

**Error**: `Phi4 not available`

**Solutions**:
1. **Install model**: `ollama pull phi4`
2. **Check installed models**: `ollama list`
3. **Verify model name**: Ensure exact spelling `phi4`

### 4. Performance Optimization

#### For Better Speed:
1. **Use GPU acceleration** (if available)
2. **Close unnecessary applications**
3. **Use smaller context window** (modify `num_ctx` in app.py)

#### System Requirements:
- **Minimum**: 4GB RAM, 4-core CPU
- **Recommended**: 8GB RAM, 6-core CPU
- **Optimal**: 32GB RAM, GPU acceleration

### 5. App-Specific Issues

#### App Won't Start:
```bash
# Check Python
python --version

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py
```

#### Browser Issues:
- Try different browser
- Clear browser cache
- Use incognito/private mode
- Check if port 7860 is blocked

### 6. Quick Diagnostics

Run these commands to check system status:

```bash
# Check Ollama status
ollama ps

# Check available models
ollama list

# Test Phi4 response
ollama run phi4 "Hello"

# Check app is running
curl http://localhost:7860
```

### 7. Alternative Models

If Phi4 is experiencing issues, try these alternatives:

```bash
# Other efficient models  
ollama pull phi3:mini      # 3.8B params, very fast
ollama pull mistral:7b     # 7B params, good balance
ollama pull gemma3:4b      # 4.3B params, fast
```

Then update `self.model_name` in `app.py` to your chosen model.

### 8. Getting Help

1. **Check logs**: Look at terminal output when app is running
2. **System resources**: Monitor RAM/CPU usage during queries
3. **Test incrementally**: Start with simple queries, increase complexity
4. **Community**: Ollama Discord/GitHub for model-specific issues

## Performance Tips

### For Financial Analysis:
- **Upload smaller datasets first** (< 1000 rows)
- **Ask specific questions** rather than "analyze everything"
- **Use clear, concise language** in prompts
- **Break complex analysis into steps**

### Prompt Optimization:
- Be specific about what you want
- Include context about your data
- Ask for code examples when needed
- Request step-by-step explanations
