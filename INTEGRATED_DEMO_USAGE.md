# EuroStyle Integrated Demo - Usage Guide

## 🎯 **Single Command Integration**

Your `start-eurostyle.sh` script now includes complete integrated demo recreation functionality! 

## 🚀 **Quick Start - Recommended Method**

```bash
cd /Users/kimvermeij/astoviq_projects/eurostyle-retail-demo
./scripts/start-eurostyle.sh --generate-integrated-demo
```

**This single command will:**
1. ✅ Start the ClickHouse containers 
2. ✅ Generate complete integrated demo environment (15-20 minutes)
3. ✅ Verify data integrity and provide summary

## 📋 **Available Options**

### **Option 1: Complete Integrated Demo (Recommended)**
```bash
./scripts/start-eurostyle.sh --generate-integrated-demo
```
- **Time**: 15-20 minutes
- **Data**: ~500MB+ across all systems
- **Includes**: HR + Operations + Finance + Webshop + POS + all integrations

### **Option 2: Basic Demo Data Only**
```bash
./scripts/start-eurostyle.sh --generate-data
```
- **Time**: 3-5 minutes  
- **Data**: ~150MB operational data only
- **Includes**: Just basic orders, customers, products

### **Option 3: Just Start Containers (No Data)**
```bash
./scripts/start-eurostyle.sh
```
- **Time**: 1-2 minutes
- **Data**: None
- **Use Case**: When you want to add data later

### **Option 4: Force Recreation**
```bash
./scripts/start-eurostyle.sh --recreate --generate-integrated-demo
```
- **Time**: 17-22 minutes
- **Data**: Fresh containers + complete integrated demo
- **Use Case**: When you want to start completely fresh

## 🌟 **What You Get with Integrated Demo**

| **System** | **Data Generated** | **Business Value** |
|------------|-------------------|-------------------|
| **Operations** | 150k customers, 50k+ orders, 1k products, 47 stores | Core business transactions |
| **Webshop** | 1.5M sessions, realistic conversion rates | Digital analytics & customer journey |
| **Finance** | GL journals, revenue reconciliation, payroll | Complete financial audit trail |
| **HR** | 447 employees, departments, performance tracking | Workforce analytics & management |
| **POS** | Employee-order linkage, commissions, shifts | Sales performance & retail operations |

## 🔗 **Cross-System Integration Features**

✅ **Orders ↔ Employees**: Every in-store sale linked to specific sales staff  
✅ **Sales ↔ Commissions**: Automatic commission calculation and GL recording  
✅ **Revenue ↔ Finance**: Perfect reconciliation between operational and financial data  
✅ **Sessions ↔ Orders**: Realistic webshop conversion with order attribution  
✅ **Employees ↔ Payroll**: Complete HR cost accounting in Finance GL  

## 📊 **Analytics Capabilities Enabled**

### **Employee Performance Analysis**
```sql
-- Revenue by employee with commission tracking
SELECT 
    e.first_name || ' ' || e.last_name as employee_name,
    p.total_sales_eur,
    p.total_commission_eur,
    p.performance_rating,
    s.store_name
FROM pos_employee_performance p
JOIN hr_employees e ON p.employee_id = e.employee_id
JOIN pos_transactions t ON p.employee_id = t.employee_id
JOIN stores s ON t.store_id = s.store_id
ORDER BY p.total_sales_eur DESC
```

### **Financial Reconciliation**
```sql
-- Verify operational revenue matches finance GL
SELECT 
    'Operations Revenue' as source,
    SUM(total_amount_eur) as amount
FROM orders 
UNION ALL
SELECT 
    'Finance GL Revenue' as source,
    SUM(credit_amount_eur) 
FROM finance_gl_journal_lines 
WHERE account_code = '4000'
```

### **Cross-System Customer Journey**
```sql
-- Complete customer journey from session to sale to finance
SELECT 
    c.customer_id,
    ws.session_id,
    o.order_id,
    pt.employee_id,
    gl.journal_header_id,
    o.total_amount_eur
FROM customers c
JOIN webshop_sessions ws ON c.customer_id = ws.customer_id  
JOIN orders o ON ws.converted_order_id = o.order_id
JOIN pos_transactions pt ON o.order_id = pt.order_id
JOIN finance_gl_journal_lines gl ON o.order_id = gl.reference_id
WHERE ws.conversion_status = 'converted'
```

## 🛠️ **Troubleshooting**

### **If Generation Fails**
1. Check that all required scripts are present in `/scripts/` directory
2. Ensure sufficient disk space (~1GB free recommended)
3. Verify Docker is running and containers are healthy
4. Check logs: `./scripts/start-eurostyle.sh > demo_log.txt 2>&1`

### **Missing Integration Scripts**
If you get "Missing required integration scripts" error:
```bash
# Verify all scripts exist
ls scripts/build_data_registry.py
ls scripts/generate_webshop_with_registry.py  
ls scripts/generate_finance_optimized.py
ls scripts/generate_hr_data.py
ls scripts/generate_hr_finance_integration.py
ls scripts/generate_pos_system.py
ls scripts/generate_pos_finance_integration.py
```

### **Performance Issues**
- **Slow Generation**: Normal for integrated demo (~15-20 min total)
- **Memory Usage**: Generation may use ~2-4GB RAM temporarily
- **Disk I/O**: SSD recommended for faster generation

## 📈 **Data Verification**

After generation completes, verify your integrated demo:

```bash
# Check data volumes
find generated_data data-generator/generated_data -name "*.csv*" -exec du -h {} \;

# Verify key integration files exist
ls -la generated_data/eurostyle_pos.transactions.csv          # POS transactions
ls -la generated_data/eurostyle_finance.gl_journal_*.csv.gz   # Finance integration  
ls -la generated_data/eurostyle_hr.employees.csv.gz           # HR data
ls -la generated_data/eurostyle_webshop.sessions.csv.gz       # Webshop analytics
```

## 🎉 **Success Indicators**

You'll know the integrated demo is ready when you see:

```
🎉 COMPLETE INTEGRATED DEMO GENERATION SUCCESSFUL! 🎉
==========================================================

Your EuroStyle integrated demo now includes:
  ✅ Complete cross-system integration (HR ↔ Operations ↔ Finance ↔ Webshop ↔ POS)
  ✅ Realistic business relationships and data volumes  
  ✅ Full audit trail and financial reconciliation
  ✅ Production-scale analytics capability
```

## 💡 **Next Steps**

Once your integrated demo is ready:

1. **Access ClickHouse**: http://localhost:8124
2. **Run Analytics Queries**: Use the SQL examples above
3. **Explore Cross-System Data**: Check the integration points
4. **Build Dashboards**: Connect your BI tools to the rich integrated dataset

---

**The integrated demo transforms your EuroStyle environment from basic demo data into a comprehensive, realistic business ecosystem perfect for advanced analytics and demonstrations!** 🚀