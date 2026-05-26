from datetime import date
from models import db, Admin, Project, Service, Testimonial, SiteSetting, Skill
from utils.helpers import slugify
import os


def seed_all(app):
    with app.app_context():
        db.create_all()
        _seed_admin(app)
        _seed_services()
        _seed_projects()
        _seed_testimonials()
        _seed_settings()
        _seed_skills()
        db.session.commit()
        print("Database seeded successfully.")


def _seed_admin(app):
    if Admin.query.first():
        return
    admin = Admin(username=app.config['ADMIN_USERNAME'])
    admin.set_password(app.config['ADMIN_PASSWORD'])
    db.session.add(admin)


def _seed_services():
    if Service.query.first():
        return
    services = [
        ('🤖 AI & Machine Learning', 'Build predictive models, classification, regression, and deep learning systems tailored to your business needs.', 'robot'),
        ('📊 Data Science & Analytics', 'Exploratory data analysis, statistical modeling, and actionable business insights from your data.', 'chart-bar'),
        ('💬 NLP Solutions', 'Text classification, sentiment analysis, chatbots, summarization, and custom NLP pipelines.', 'chat'),
        ('🔍 RAG Systems', 'Document Q&A, knowledge base AI, LLM integrations, and retrieval-augmented generation systems.', 'search'),
        ('⚡ Python Automation', 'Web scraping, workflow automation, ETL pipelines, and task scheduling solutions.', 'bolt'),
        ('📈 Interactive Dashboards', 'Power BI, Streamlit, and Plotly-based dashboards for real-time data visualization.', 'trending-up'),
    ]
    for i, (title, desc, icon) in enumerate(services, 1):
        svc = Service(
            title=title,
            slug=slugify(title),
            description=desc,
            icon=icon,
            order=i,
            visible=True,
            pricing_basic='Contact for pricing',
            pricing_standard='Contact for pricing',
            pricing_premium='Contact for pricing',
        )
        db.session.add(svc)


def _seed_projects():
    if Project.query.first():
        return
    projects = [
        {
            'title': 'Sales Forecasting Dashboard',
            'category': 'Dashboard',
            'short_desc': 'End-to-end sales forecasting with interactive Streamlit dashboard and Plotly charts.',
            'full_desc': '<p>Built a comprehensive sales forecasting system using ARIMA and Prophet models integrated into an interactive Streamlit dashboard. The dashboard provides real-time insights into sales trends, seasonality, and future projections.</p>',
            'tech_stack': 'Python, Pandas, Streamlit, Plotly, Prophet, ARIMA',
            'client_name': 'Retail Client',
            'client_country': 'United States',
            'results': 'Reduced forecasting error by 35%, saving 10+ hours of manual analysis weekly.',
            'featured': True,
        },
        {
            'title': 'Customer Sentiment Analyzer',
            'category': 'NLP',
            'short_desc': 'BERT-based sentiment analysis system for customer reviews with 94% accuracy.',
            'full_desc': '<p>Developed a fine-tuned BERT model for multi-class sentiment analysis of customer reviews. Integrated with a Flask REST API for real-time analysis and batch processing capabilities.</p>',
            'tech_stack': 'NLP, BERT, Python, Flask, Transformers, PostgreSQL',
            'client_name': 'E-commerce Client',
            'client_country': 'United Kingdom',
            'results': 'Achieved 94% accuracy, processing 50,000+ reviews automatically.',
            'featured': True,
        },
        {
            'title': 'Document Q&A System',
            'category': 'AI',
            'short_desc': 'RAG-based document intelligence system using LangChain and OpenAI GPT.',
            'full_desc': '<p>Built a production-ready Retrieval-Augmented Generation system enabling natural language querying of large document collections. Features semantic search, citation tracking, and conversation history.</p>',
            'tech_stack': 'RAG, LangChain, OpenAI, Python, FAISS, FastAPI',
            'client_name': 'Legal Tech Startup',
            'client_country': 'Canada',
            'results': 'Reduced document review time by 70%, processing 1000+ page documents instantly.',
            'featured': True,
        },
        {
            'title': 'Automated ETL Pipeline',
            'category': 'Automation',
            'short_desc': 'Scalable ETL pipeline with Apache Airflow for automated data processing.',
            'full_desc': '<p>Designed and implemented a fault-tolerant ETL pipeline using Apache Airflow for orchestration, with automated data quality checks, error alerting, and comprehensive logging.</p>',
            'tech_stack': 'Python, Airflow, PostgreSQL, Docker, pandas, SQLAlchemy',
            'client_name': 'FinTech Client',
            'client_country': 'Australia',
            'results': 'Automated 8 hours of daily manual data processing, 99.9% uptime.',
            'featured': False,
        },
    ]
    for p in projects:
        proj = Project(
            title=p['title'],
            slug=slugify(p['title']),
            category=p['category'],
            short_desc=p['short_desc'],
            full_desc=p['full_desc'],
            tech_stack=p['tech_stack'],
            client_name=p['client_name'],
            client_country=p['client_country'],
            results=p['results'],
            featured=p.get('featured', False),
            status='published',
            project_date=date(2024, 1, 1),
        )
        db.session.add(proj)


def _seed_testimonials():
    if Testimonial.query.first():
        return
    testimonials = [
        ('James Wilson', 'RetailCo Inc.', 'United States', 5, 'Kinjal delivered an outstanding sales forecasting dashboard. The quality of work exceeded our expectations, and she was responsive throughout the project. Highly recommended!'),
        ('Sarah Thompson', 'TechShop UK', 'United Kingdom', 5, 'The sentiment analyzer has transformed how we handle customer feedback. Exceptional Python and NLP skills. Will definitely hire again for future projects.'),
        ('Michael Chen', 'LegalAI Corp', 'Canada', 5, 'The RAG system Kinjal built is incredible. It\'s processing our legal documents faster than we thought possible. Professional, timely, and technically brilliant.'),
        ('Emma Rodriguez', 'FinData Pty', 'Australia', 5, 'The ETL pipeline has saved us countless hours of manual work. Kinjal understood our requirements perfectly and delivered a robust, well-documented solution.'),
    ]
    for name, company, country, rating, text in testimonials:
        t = Testimonial(client_name=name, company=company, country=country, rating=rating, text=text, visible=True, date=date(2024, 6, 1))
        db.session.add(t)


def _seed_settings():
    if SiteSetting.query.first():
        return
    settings = {
        'business_name': 'JK Data Lab',
        'tagline': 'Transforming Data Into Intelligence',
        'email': 'kinjal@jkdatalab.com',
        'phone': '+91-9157938887',
        'address': 'C 102 Aaron Elegance, New C.G. Road, Chandkheda, Ahmedabad, Gujarat - 382424, India',
        'whatsapp': '919157938887',
        'linkedin': 'https://linkedin.com/in/kinjaljayswal',
        'github': 'https://github.com/kinjaljayswal',
        'upwork': 'https://upwork.com/freelancers/kinjaljayswal',
        'fiverr': 'https://fiverr.com/kinjaljayswal',
        'calendly': 'https://calendly.com/kinjal-jkdatalab',
        'meta_title': 'JK Data Lab — AI & Data Science Freelancing',
        'meta_description': 'Professional AI, Data Science, NLP, and RAG solutions by JK Data Lab. Based in Ahmedabad, serving global clients.',
        'meta_keywords': 'AI, data science, NLP, RAG, Python, machine learning, freelancer, India',
        'google_analytics': '',
        'hero_headline': 'Transforming Raw Data Into Business Intelligence',
        'hero_subheadline': 'AI · Data Science · NLP · RAG Solutions delivered by JK Data Lab',
        'stat_projects': '50+',
        'stat_clients': '30+',
        'stat_countries': '10+',
        'stat_years': '5+',
        'udyam': 'UDYAM-GJ-01-0638170',
    }
    for k, v in settings.items():
        db.session.add(SiteSetting(key=k, value=v))


def _seed_skills():
    if Skill.query.first():
        return
    skills = [
        ('Python', 'Programming', 95),
        ('Machine Learning', 'AI/ML', 90),
        ('Deep Learning', 'AI/ML', 85),
        ('NLP', 'AI/ML', 88),
        ('LangChain / RAG', 'AI/ML', 85),
        ('Pandas & NumPy', 'Data Science', 95),
        ('SQL', 'Data Science', 90),
        ('Power BI', 'Visualization', 85),
        ('Streamlit', 'Visualization', 90),
        ('Plotly', 'Visualization', 88),
        ('Flask', 'Web', 85),
        ('FastAPI', 'Web', 80),
        ('Docker', 'DevOps', 75),
        ('Git', 'DevOps', 90),
        ('TensorFlow', 'AI/ML', 80),
        ('Scikit-learn', 'AI/ML', 92),
    ]
    for i, (name, cat, prof) in enumerate(skills, 1):
        db.session.add(Skill(name=name, category=cat, proficiency=prof, order=i))
