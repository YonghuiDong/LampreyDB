# 安装python3，开始使用的版本是 v3.7.4

[python 3.7.0 安装配置方法图文教程](http://www.manongjc.com/article/8260.html)

注意 **勾选 将 python 加入 path**

# 创建并激活虚拟环境
windows 10 系统下操作方法
```
python -m venv env
cmd
env\Scripts\activate
```

# 安装依赖包
```
pip install -r requirements.txt
```

# 使用 mysql 数据库

这个教程写的还不错： https://www.cnblogs.com/wcwnina/p/8719482.html

修改 chemistryManage\settings.py 关于数据库的配置, 并添加如下的语句
```python
import pymysql  # 使用三方开源驱动
pymysql.install_as_MySQLdb()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'mydb',         # 你要存储数据的库名，事先要创建之
        'USER': 'root',         # 数据库用户名
        'PASSWORD': '1234',     # 密码
        'HOST': 'localhost',    # 主机
        'PORT': '3306',         # 数据库使用的端口
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

```
### 创建数据库用户
```
create user analyze_user identified by "analyze_password";
create database analyze_base character set utf8mb4;
grant all privileges on analyze_base.* to 'analyze_user'@'%' identified by 'analyze_password' with grant option;
flush privileges;

```

### 问题解决
- `raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)`

打开 env/lib/python3.7/site-packages/django/db/backends/mysql/base.py 文件浏览至 35、36 行， 把
```
version = Database.version_info
if version < (1, 3, 13):
    raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
```
改成
```
version = Database.version_info
if version < (1, 3, 12):
    raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
```
- `AttributeError: 'str' object has no attribute 'decode'`
打开 `env/lib/python3.7/site-packages/django/db/backends/mysql/operations.py` 文件浏览至宝 145、146 行， 把
```
        if query is not None:
            query = query.decode(errors='replace')
```
改成
```
        if query is not None:
            if type(query) == bytes:
                query = query.decode(errors='replace')  # mysqlclient
            elif type(query) == str:
                query = query.encode(errors='replace')  # PyMySQL
            else:
                from django.utils.encoding import force_text
                query = force_text(query, errors='replace')  # fallback compatibility ?
```
- 原因解释
  - 默认支持 mysqlclient， 但是 mysqlclient 不支持 py3
  - 版本问题
  - 默认编码问题 
  参考 https://github.com/PyMySQL/PyMySQL/issues/790 和 https://www.cnblogs.com/linkenpark/p/10907578.html


# 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 数据库导入导出
把sqlite中的数据导出到其他数据库
```
python manage.py dumpdata -> initial_data.json
```

```
python manage.py dumpdata --exclude=contenttypes --exclude=auth.Permission > initial_data.json
```

了解更多参考 [Django数据迁移](https://www.jianshu.com/p/ef971ac0131f)

# 创建管理员账号

```bash
python manege.py createsuperuser
```

# 启动网站
```
python manage.py runserver 0.0.0.0:8000
```

# 访问网站

http://127.0.0.1:8000
http://server_ip_or_domain:8000


