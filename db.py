# db.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    schedule_type = Column(String, nullable=False)  # 'fixed' 或 'random'
    days = Column(Integer)
    exec_time = Column(String)
    schedule = Column(String)
    interval = Column(Integer)
    data_format = Column(String, nullable=False)
    ignore_comment = Column(Boolean, default=False),
    table_type = Column(Integer, default=0)
    parse_values = Column(JSON)
    fixed_values = Column(JSON)
    is_active = Column(Boolean, default=False)
    create_time = Column(DateTime, default=datetime.datetime.now)
    last_run_time = Column(DateTime)

# 数据库初始化
engine = create_engine('sqlite:///data/tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)