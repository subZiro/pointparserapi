"""
Модели хранения истории поиска точек
"""

from datetime import datetime

from app import db


class SearchHistory(db.Model):
    """История поисковых запросов к парсерам."""
    __tablename__ = 'tb_search_histories'
    __table_args__ = {
        'schema': 'parsers'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parser_id = db.Column(db.Integer, db.ForeignKey('parsers.tb_parsers_details.pid'), index=True)
    search_query = db.Column(db.String)
    cnt_results = db.Column(db.Integer)
    is_complete = db.Column(db.Boolean, default=False)
    skip = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now)


class ParserDetail(db.Model):
    """Модель парсера, с ограничениям по лимитам запросов к апи."""
    __tablename__ = 'tb_parsers_details'
    __table_args__ = {
        'schema': 'parsers'
    }
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parser_type = db.Column(db.String, nullable=False)
    caption = db.Column(db.Text, nullable=False)
    count = db.Column(db.Integer, default=0)  # использовано обращений в текущую дату
    limit = db.Column(db.Integer, nullable=False)  # лимит запросов
    last_update = db.Column(db.DateTime, default=datetime.now)

    search_history = db.relationship('SearchHistory', backref='parser', lazy='dynamic')

    @property
    def ping(self):
        """Увеличение счетчика текущего дня."""

        now = datetime.now().date()
        if self.last_update.date() != now:
            self.count = 0

        if self.count < self.limit:
            self.count += 1
            self.last_update = now
            db.session.commit()
            return True
        return False
