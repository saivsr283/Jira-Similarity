# 🔐 JIRA Authentication Issue - Solution Guide

## 🎯 **Issue Identified**

The Docker container is working perfectly, but there's an **authentication issue** with your JIRA credentials.

### ❌ **Current Problem:**
- **401 Unauthorized** error when accessing JIRA API
- Ticket PLAT-44192 exists at [https://koreteam.atlassian.net/browse/PLAT-44192](https://koreteam.atlassian.net/browse/PLAT-44192) ✅
- But API access is failing ❌

## 🔍 **Root Cause Analysis**

The diagnostic shows:
```
Status: 401
❌ Authentication failed (401)
```

**Most likely issues:**
1. **Username format** - Should be email address, not domain
2. **API token** - May be expired or incorrect
3. **Permissions** - Token may lack API access rights

## 🛠️ **Solution Steps**

### **Step 1: Fix Username Format**
Your current config has:
```json
{
  "username": "hemanth.bandaru@kore.com"
}
```

**Should be:**
```json
{
  "username": "hemanth.bandaru@company.com"
}
```

### **Step 2: Verify API Token**
1. Go to [Atlassian Account Settings](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Generate a new API token
3. Ensure it has **read permissions** for JIRA

### **Step 3: Update Configuration**

**Option A: Edit config.json**
```bash
# Edit the config file
nano config.json

# Update username to email format
# Update API token if needed
```

**Option B: Use Environment Variables**
```bash
export JIRA_URL="https://koreteam.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-new-api-token"
```

## 🧪 **Test the Fix**

### **1. Test Credentials**
```bash
sudo docker run --rm --entrypoint python \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/test_credentials.py:/app/test_credentials.py:ro" \
  jira-similarity-tool test_credentials.py
```

### **2. Test Ticket Access**
```bash
./docker-run.sh analyze PLAT-44192
```

### **3. Expected Success Output**
```
✅ Success! User: Your Name
   Email: your-email@company.com

Target Ticket: PLAT-44192
Summary: [Ticket summary]
Type: [Issue type]
Priority: [Priority]
Status: [Status]

Found X similar tickets:
1. PLAT-XXXXX (Similarity: 0.XXX)
   Summary: [Similar ticket summary]
   URL: https://koreteam.atlassian.net/browse/PLAT-XXXXX
```

## 📋 **Common Username Formats**

| Current | Should Be |
|---------|-----------|
| `hemanth.bandaru@kore.com` | `hemanth.bandaru@company.com` |
| `hemanth.bandaru` | `hemanth.bandaru@company.com` |
| `hemanth` | `hemanth@company.com` |

## 🔧 **API Token Requirements**

Your API token needs these permissions:
- ✅ **Read** access to JIRA projects
- ✅ **Read** access to issues
- ✅ **Read** access to user information

## 🚀 **Quick Fix Commands**

```bash
# 1. Update config.json with correct email
sed -i 's/"hemanth.bandaru@kore.com"/"hemanth.bandaru@company.com"/' config.json

# 2. Test credentials
sudo docker run --rm --entrypoint python \
  -v "$(pwd)/config.json:/app/config.json:ro" \
  -v "$(pwd)/test_credentials.py:/app/test_credentials.py:ro" \
  jira-similarity-tool test_credentials.py

# 3. Test ticket analysis
./docker-run.sh analyze PLAT-44192
```

## ✅ **Success Indicators**

When fixed, you should see:
- ✅ **200 status** on credential test
- ✅ **User information** displayed
- ✅ **Ticket details** retrieved
- ✅ **Similar tickets** found

## 📞 **Still Having Issues?**

If authentication still fails:
1. **Double-check email format**
2. **Generate new API token**
3. **Verify JIRA instance URL**
4. **Check user permissions in JIRA**

---

**The Docker setup is perfect - just need to fix the credentials!** 🐳✨ 