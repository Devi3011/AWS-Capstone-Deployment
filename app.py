from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'neural-career-matrix-2026-super-secure'

DATA_FILE = "registrations.json"

# ---------------- UPDATED MODULE & 10-QUESTION QUIZ DATA ----------------
COURSE_DATA = {
    "AWS Cloud Practitioner": {
        "videos": [
            {"title": "Module 1: Cloud Concepts Essentials", "link": "https://www.youtube.com"},
            {"title": "Module 2: AWS Security & IAM", "link": "https://www.youtube.com"},
            {"title": "Module 3: Billing & Pricing Models", "link": "https://www.youtube.com"}
        ],
        "quiz": [
            {"q": "1. What is the AWS pay-as-you-go pricing model called?", "options": ["Fixed Cost", "On-demand Pricing", "Annual Contract", "Prepaid"], "ans": 1},
            {"q": "2. Which service is used for object storage?", "options": ["EC2", "RDS", "S3", "VPC"], "ans": 2},
            {"q": "3. What does IAM stand for?", "options": ["Identity and Access Management", "Internal Asset Manager", "Internet Access Method", "Instant Account Maker"], "ans": 0},
            {"q": "4. Which is a Global service in AWS?", "options": ["EC2", "S3", "IAM", "Subnet"], "ans": 2},
            {"q": "5. What is the AWS shared responsibility model?", "options": ["AWS does everything", "User does everything", "Shared security duties", "None"], "ans": 2},
            {"q": "6. Which service provides DNS web service?", "options": ["Route 53", "CloudFront", "Direct Connect", "VPC"], "ans": 0},
            {"q": "7. What is an Availability Zone?", "options": ["A whole country", "One or more data centers", "A virtual server", "A hard drive"], "ans": 1},
            {"q": "8. Which tool estimates AWS costs?", "options": ["Inspector", "Pricing Calculator", "Shield", "CloudTrail"], "ans": 1},
            {"q": "9. What provides protection against DDoS?", "options": ["AWS Shield", "AWS Config", "AWS Artifact", "AWS Glue"], "ans": 0},
            {"q": "10. Which service is used for NoSQL databases?", "options": ["RDS", "DynamoDB", "Redshift", "ElastiCache"], "ans": 1}
        ]
    },
    "AWS Solutions Architect Associate": {
        "videos": [
            {"title": "Module 1: VPC Networking Deep Dive", "link": "https://www.youtube.com"},
            {"title": "Module 2: High Availability (ELB & ASG)", "link": "https://www.youtube.com"},
            {"title": "Module 3: S3 & Storage Options", "link": "https://www.youtube.com"}
        ],
        "quiz": [
            {"q": "1. Which load balancer works at Layer 7?", "options": ["ALB", "NLB", "CLB", "GWLB"], "ans": 0},
            {"q": "2. S3 storage class for archiving data for months?", "options": ["Standard", "Intelligent Tiering", "Glacier", "One Zone"], "ans": 2},
            {"q": "3. What is the purpose of Auto Scaling?", "options": ["Fault Tolerance", "Elasticity", "Cost Savings", "All the above"], "ans": 3},
            {"q": "4. Where are S3 buckets created?", "options": ["Regionally", "Globally", "In an AZ", "On-premise"], "ans": 1},
            {"q": "5. What does VPC stand for?", "options": ["Virtual Private Cloud", "Visual Private Core", "Virtual Public Computer", "None"], "ans": 0},
            {"q": "6. Which service provides content delivery (CDN)?", "options": ["CloudFront", "Route 53", "Direct Connect", "VPC"], "ans": 0},
            {"q": "7. What is a NACL?", "options": ["Stateless firewall", "Stateful firewall", "Database", "Compute service"], "ans": 0},
            {"q": "8. Which service is a fully managed NoSQL database?", "options": ["RDS", "Aurora", "DynamoDB", "Redshift"], "ans": 2},
            {"q": "9. What is the 'R' in RDS?", "options": ["Remote", "Relational", "Route", "Rapid"], "ans": 1},
            {"q": "10. How to connect on-premise to AWS privately?", "options": ["Internet Gateway", "Direct Connect", "VPC Peering", "NAT Gateway"], "ans": 1}
        ]
    },
    "AWS Developer Associate": {
        "videos": [
            {"title": "Module 1: AWS SDK & CLI Basics", "link": "https://www.youtube.com"},
            {"title": "Module 2: Serverless Logic (Lambda)", "link": "https://www.youtube.com"},
            {"title": "Module 3: DynamoDB for Developers", "link": "https://www.youtube.com"}
        ],
        "quiz": [
            {"q": "1. Which service is 'Serverless'?", "options": ["EC2", "Lambda", "RDS", "EBS"], "ans": 1},
            {"q": "2. What is the default timeout for Lambda?", "options": ["3 seconds", "15 minutes", "1 minute", "30 seconds"], "ans": 0},
            {"q": "3. Which CLI command lists S3 buckets?", "options": ["aws s3 ls", "aws s3 list", "aws s3 get", "aws s3 show"], "ans": 0},
            {"q": "4. What is an Inline Policy?", "options": ["Shared policy", "Policy for single user/group", "AWS Managed", "None"], "ans": 1},
            {"q": "5. What is the primary key in DynamoDB?", "options": ["Partition Key only", "Sort Key only", "Partition & Sort Key", "Both A and C"], "ans": 3},
            {"q": "6. Which service is used for API management?", "options": ["API Gateway", "Route 53", "CloudFront", "SNS"], "ans": 0},
            {"q": "7. What is an AWS SDK?", "options": ["Software Dev Kit", "System Dev Kit", "Storage Dev Kit", "None"], "ans": 0},
            {"q": "8. Which service provides message queuing?", "options": ["SNS", "SQS", "SES", "SWF"], "ans": 1},
            {"q": "9. What is X-Ray used for?", "options": ["Storage", "Debugging/Tracing", "Compute", "Security"], "ans": 1},
            {"q": "10. What is Elastic Beanstalk?", "options": ["PaaS", "IaaS", "SaaS", "DBaaS"], "ans": 0}
        ]
    },
    "AWS SysOps Administrator": {
        "videos": [
            {"title": "Module 1: CloudWatch Monitoring", "link": "https://www.youtube.com"},
            {"title": "Module 2: CloudFormation Automation", "link": "https://www.youtube.com"},
            {"title": "Module 3: High Availability & Scaling", "link": "https://www.youtube.com"}
        ],
        "quiz": [
            {"q": "1. Which tool is for monitoring resources?", "options": ["CloudWatch", "S3", "VPC", "IAM"], "ans": 0},
            {"q": "2. What is a CloudWatch Metric?", "options": ["A time-ordered set of data", "A database", "A server", "None"], "ans": 0},
            {"q": "3. What is AWS CloudTrail?", "options": ["Monitoring", "Logging API calls", "Storage", "Compute"], "ans": 1},
            {"q": "4. What is used for Infrastructure as Code?", "options": ["CloudFormation", "EC2", "S3", "Route 53"], "ans": 0},
            {"q": "5. What is a Golden Image?", "options": ["A customized AMI", "A new S3 bucket", "A VPC", "None"], "ans": 0},
            {"q": "6. Which service helps with compliance?", "options": ["AWS Config", "S3", "EC2", "IAM"], "ans": 0},
            {"q": "7. What is the purpose of ELB?", "options": ["Distribute traffic", "Store data", "Run code", "None"], "ans": 0},
            {"q": "8. What is a Bastion Host?", "options": ["Secure entry point", "Database", "Storage", "Web server"], "ans": 0},
            {"q": "9. Which service automates patching?", "options": ["Systems Manager", "IAM", "VPC", "S3"], "ans": 0},
            {"q": "10. What is an AWS Health Dashboard?", "options": ["Status of AWS services", "Personal health", "Storage info", "None"], "ans": 0}
        ]
    },
    "AWS DevOps Engineer Professional": {
        "videos": [
            {"title": "Module 1: CI/CD with CodePipeline", "link": "https://www.youtube.com"},
            {"title": "Module 2: Infrastructure as Code (CDK)", "link": "https://www.youtube.com"},
            {"title": "Module 3: Advanced Deployment Strategies", "link": "https://www.youtube.com"}
        ],
        "quiz": [
            {"q": "1. Which service is for CI/CD?", "options": ["CodePipeline", "S3", "EC2", "RDS"], "ans": 0},
            {"q": "2. What is a Blue/Green deployment?", "options": ["Running two environments", "Upgrading one server", "Deleting old data", "None"], "ans": 0},
            {"q": "3. What is CodeBuild used for?", "options": ["Compiling code", "Storing code", "Deploying code", "None"], "ans": 0},
            {"q": "4. What is CodeCommit?", "options": ["Source control (Git)", "Build tool", "Deploy tool", "None"], "ans": 0},
            {"q": "5. What is AWS CDK?", "options": ["Cloud Dev Kit", "Compute Dev Kit", "Code Dev Kit", "None"], "ans": 0},
            {"q": "6. Which tool handles configuration management?", "options": ["OpsWorks", "S3", "VPC", "IAM"], "ans": 0},
            {"q": "7. What is Canary Deployment?", "options": ["Partial rollout", "Full rollout", "No rollout", "None"], "ans": 0},
            {"q": "8. What is a Buildspec file?", "options": ["YAML for CodeBuild", "JSON for S3", "Python for EC2", "None"], "ans": 0},
            {"q": "9. Which service automates resource provisioning?", "options": ["CloudFormation", "IAM", "S3", "RDS"], "ans": 0},
            {"q": "10. What is AWS Artifact?", "options": ["Compliance reports", "Build tool", "Source control", "None"], "ans": 0}
        ]
    }
}

# ---------------- HELPERS ----------------

def is_logged_in():
    return 'username' in session

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- ROUTES ----------------

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').lower().strip()
        password = request.form.get('password', '').strip()
        if username == 'virtual career' and password == 'counselor':
            session['username'] = username
            flash('🚀 Welcome!', 'success')
            return redirect(url_for('dashboard'))
        flash('❌ Invalid Login', 'error')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/aws_register', methods=['GET', 'POST'])
def aws_register():
    if not is_logged_in(): return redirect(url_for('login'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        courses = request.form.getlist('courses')

        data = load_data()
        student = {"name": f"{first_name} {last_name}", "email": email, "phone": phone, "courses": ", ".join(courses)}
        data.append(student)
        save_data(data)

        # Registration success aana udane select panna first course-kku redirect
        main_course = courses[0] if courses else "AWS Cloud Practitioner"
        flash('✅ Registration Success!', 'success')
        return redirect(url_for('career_path', name=first_name, course=main_course))
    return render_template('AWS_register.html')

@app.route('/aws_list')
def aws_list():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('Register_list.html', registrations=load_data())

@app.route('/career path')
def career_path():
    if not is_logged_in(): return redirect(url_for('login'))
    name = request.args.get('name', 'User')
    course = request.args.get('course', 'AWS Cloud Practitioner')
    
    # 10 questions and video modules info inge pass aagum
    info = COURSE_DATA.get(course)
    return render_template('career path.html', name=name, course=course, info=info)

# --- COURSE RECOMMENDATIONS ---
@app.route('/course_recommendations', methods=['GET', 'POST'])
def recommendations():
    if not is_logged_in(): return redirect(url_for('login'))
    if request.method == 'POST':
        selected = request.form.getlist('courses')
        if not selected:
            flash("Please select at least one course!", "danger")
        else:
            flash(f"Successfully Enrolled in {len(selected)} Courses! 🚀", "success")
        return redirect(url_for('recommendations'))
    return render_template('course_recommended.html')

@app.route('/job_recommendations')
def job_recommendations():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('job_recommended.html')

@app.route('/counsel')
def counsel():
    if not is_logged_in(): return redirect(url_for('login'))
    return render_template('counsel.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/AWS Learning Dashboard')
def aws_learning_dashboard():
    return render_template('AWS Learning Dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
