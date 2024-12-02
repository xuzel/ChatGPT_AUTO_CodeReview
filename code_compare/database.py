import pickle
import os


class Database:
    def __init__(self, filename='database.pkl'):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        """从.pkl文件加载数据，如果文件不存在，返回空字典"""
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as f:
                return pickle.load(f)
        else:
            return {}

    def save_data(self):
        """将数据保存到.pkl文件"""
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data, f)

    def add_record(self, key, value):
        """向数据库中添加一条记录"""
        self.data[key] = value
        self.save_data()

    def get_record(self, key):
        """根据key获取数据库中的记录"""
        return self.data.get(key, None)

    def delete_record(self, key):
        """根据key删除数据库中的记录"""
        if key in self.data:
            del self.data[key]
            self.save_data()

    def __repr__(self):
        """打印数据库的内容"""
        return str(self.data)
