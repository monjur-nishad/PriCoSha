from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
import  hashlib

app = Flask(__name__)

conn = pymysql.connect(host='localhost',
                       port=8889,
                       user='root',
                       password='root',
                       db='PriCoSha',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
@app.route('/')
def hello():
	return render_template('index.html')

@app.route('/addfriend')
def addfriend():

    cursor = conn.cursor()
    username = session['username']
    query = 'select count(group_name) as no From FriendGroup where username = %s'
    cursor.execute(query, username)
    data2 = cursor.fetchall()
    for line in data2:
      if str(line['no']) == str(0):
        error_nogroup = "Sorry You Don't Have Any FriendGroup Yet"
        return render_template("confirm.html", error_nogroup=error_nogroup)

    cursor2 = conn.cursor()
    query2 = 'select group_name From FriendGroup where username = %s'
    cursor.execute(query2, username)
    data = cursor.fetchall()
    return render_template('addfriend.html', data=data)

@app.route('/unfriend')
def unfriend():
    cursor = conn.cursor()
    username = session['username']
    query = 'Select count(group_name) as no From FriendGroup where username = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()
    for line in data:
      if str(line['no']) == str(0):
        error_nogroup = "Sorry You Don't Have Any FriendGroup Yet"
        return render_template("confirm.html", error_nogroup=error_nogroup)

    cursor2 = conn.cursor()
    query2 = 'select group_name From FriendGroup where username = %s'
    cursor.execute(query2, username)
    data = cursor.fetchall()
    return render_template('unfriend.html', data=data)


@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/confirm')
def confirm():
	return render_template('confirm.html')

@app.route('/post')
def postpage():
	return render_template('post.html')

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():

	username = request.form['username']
	password = request.form['password']
	cursor = conn.cursor()
	query = 'SELECT * FROM Person WHERE username = %s and password = %s'
	cursor.execute(query, (username, hashlib.md5(password).hexdigest()))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		session['username'] = username
		return redirect(url_for('home'))
	else:
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	
	username = request.form['username']
	password = request.form['password']
    #password = hashlib.md5(password_text).hexdigest()
	firstname = request.form['fname']
	lastname = request.form['lname']
	cursor = conn.cursor()
	query = 'SELECT * FROM Person WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s)'
		cursor.execute(ins, (username, hashlib.md5(password).hexdigest(),firstname,lastname))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    username = session['username']
    sql ="select id, content_name, file_path,timest, public from Content  where id in (select distinct(id) from content  where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) order by timest DESC"
    cursor = conn.cursor()
    cursor.execute(sql, (username))
    #data = cursor.fetchall()
    data = cursor.fetchall()

    cursor2 = conn.cursor()
    sql2 = 'Select id,username,comment_text from  Comment where id in (select distinct(id) from content   where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s) )'
    cursor2.execute(sql2, (username))
    data2 = cursor2.fetchall()

    a = []
    for line in data:
        ids = line['id']
        cursor3 = conn.cursor()
        sql3 = """Select id, first_name, last_name from(select id, username_taggee as username From Tag where id = %s and status ="1") as new natural join Person"""
        cursor3.execute(sql3, ids)
        last = cursor3.fetchall()
        a.append(last)

    data3 = []
    for line in a:
        for line2 in line:
            data3.append(line2)

    #sql3 = 'select id, first_name,last_name from((select distinct(id), first_name,last_name from content natural join Person where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) as sub  natural join tag) where status = "1" and username_tagee = %s'
    #cursor3.execute(sql3, (username))
    #data3 = cursor3.fetchall()

    cursor4 = conn.cursor()
    sql4 = """select id, first_name,last_name,username_tagger from((select distinct(id), first_name,last_name from content natural join Person where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) as sub  natural join tag) where status="0" and username_taggee = %s"""
#     sql4 = """select id, first_name,last_name,username_tagger
# from((select distinct(id), first_name,last_name
# from content natural join Person
# where public = true or id in
#     		(select DISTINCT(id)
# 				from Member join Share using(group_name)
# 				where Member.username = %s)) as sub  natural join tag) where status="0" and username_taggee = %s """
    cursor4.execute(sql4, (username, username))
    data4 = cursor4.fetchall()


    return render_template('home.html', username=username, data=data, data2=data2, data3=data3 , data4 = data4)

# @app.route('/postform', methods=['GET', 'POST'])
# def postform():
#     title = request.form['title']
#     username = session['username']
#     state = request.form['privacy']
#     cursor = conn.cursor()
#
#     if str(state) == "0":
#         cursor = conn.cursor()
#         query = 'Select group_name From FriendGroup where username = %s'
#         cursor.execute(query, username)
#         data = cursor.fetchall()
#         if(data):
#             return render_template('post.html', data=data)
#         else:
#             errorpost = "This User Doesn't own any FriendGroup"
#             return render_template('confirm.html', errorpost=errorpost)
#
#     if str(state) == "1":
#         cursor2 = conn.cursor()
#         query2 = 'INSERT INTO Content(username,content_name,public) VALUES(%s, %s,%s)'
#         cursor2.execute(query2, (username, title, state))
#         conn.commit()
#         cursor2.close()
#         msg = 'You have made a new public post!!'
#         return render_template('post.html', msg=msg)

@app.route('/postform', methods=['GET', 'POST'])
def post():
    title = request.form['title']
    username = session['username']
    state = request.form['privacy']
    cursor = conn.cursor()
    query = 'INSERT INTO Content(username,content_name,public) VALUES(%s, %s,%s)'
    cursor.execute(query, (username, title, state))
    conn.commit()
    cursor.close()
    if str(state) == "0":
        cursor2 = conn.cursor()
        query2 = 'Select group_name From FriendGroup where username = %s'
        cursor2.execute(query2, username)
        data = cursor2.fetchall()
        if data:
            msg ="Private post made"
            return render_template('post.html', data=data, msg=msg)
        else:
            error_nofriend = "This User Doesn't own any FriendGroup"
            return render_template('confirm.html', error_nofriend=error_nofriend)
    else:
        msg = 'You have made a new public post!!'
        return render_template('post.html', msg=msg)

@app.route('/selectgroup', methods=['GET', 'POST'])
def selectgroup():
    multiselect = request.form.getlist('mymultiselect')
    cursor = conn.cursor()
    query = 'Select max(id) From Content'
    cursor.execute(query)
    data = cursor.fetchone()
    data2 = data[u'max(id)']

    username = session['username']
    query = 'INSERT INTO Share VALUES(%s, %s,%s)'
    for group in multiselect:
        cursor = conn.cursor()
        cursor.execute(query, (data2, group, username))
        conn.commit()
        cursor.close()
    return render_template('post.html')

@app.route('/selectgroup2', methods=['GET', 'POST'])
def selectgroup2():

    fname = request.form['first_name']
    lname = request.form['last_name']
    gname = request.form['group']
    #member_name = request.form['username']
    cursor = conn.cursor()
    sql = 'Select username, count(*) as no from Person where first_name = %s and last_name  = %s'
    cursor.execute(sql, (fname, lname))
    datax = cursor.fetchone()
    cname = datax['username']
    creator = session['username']

    cursor = conn.cursor()
    username = session['username']
    query = 'Select group_name From FriendGroup where username = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()

    if str(datax['no']) == str(1):

        cursor3 = conn.cursor()
        sql3 = "Select count(*) as no2 From Person natural join Member where first_name = %s and last_name = %s and group_name = %s"
        cursor3.execute(sql3, (fname, lname, gname))
        #cursor.execute()
        datac = cursor3.fetchone()

        #return render_template("confirm.html", datac=datac)
        if str(datac['no2']) == str(1):
            errorz = "User already exists"
            return render_template('confirm.html', erroz=errorz)
        else:
            cursor3 = conn.cursor()
            sql3 = "select username from Person where first_name = %s and last_name =%s"
            cursor3.execute(sql3, (fname, lname))
            names = cursor3.fetchone()
            ucc = names['username']
            cursor2 = conn.cursor()
            sql2 = 'insert into Member values(%s,%s,%s)'
            msgt = "User Added"
            cursor2.execute(sql2, (ucc, gname, creator))
            conn.commit()
            cursor2.close()
            return render_template('confirm.html', msgt=msgt)

    if datax['no'] > 1:
        errorx = "Sorry. There are mutiple people with same name. To proceed enter username"
        return render_template('insertusername.html', errorx=errorx, data=data)

@app.route('/selectgroup3', methods=['GET', 'POST'])
def selectgroup3():
    fname = request.form['first_name']
    lname = request.form['last_name']
    gname = request.form['group']
    member_name = request.form['username']
    cname = session['username']

    cursor = conn.cursor()
    username = session['username']
    query = 'Select group_name From FriendGroup where username = %s'
    cursor.execute(query, username)
    data = cursor.fetchall()

    cursor3 = conn.cursor()
    sql3 = "Select count(*) as no2 From Member where username = %s and group_name = %s and username_creator = %s"
    cursor3.execute(sql3, (member_name, gname, cname))
    # cursor.execute()
    datac = cursor3.fetchone()
    if str(datac['no2']) == str(1):
        errorz = "User already exists"
        return render_template('confirm.html', erroz=errorz)
    else:
        cursor2 = conn.cursor()
        sql2 = 'insert into Member values(%s,%s,%s)'
        cursor2.execute(sql2, (member_name, gname, cname))
        conn.commit()
        cursor2.close()
        return render_template('confirm.html')

@app.route('/tagconfirm', methods=['GET', 'POST'])
def tagconfirm():
    state = request.form['status']
    cid = request.form['id']
    username = session['username']
    tagger = request.form['tagger']
    cursor = conn.cursor()
    cursor2 = conn.cursor()

    if state == "1":
        query = "update Tag set status = 1 where id = %s"
        cursor.execute(query, cid)
        conn.commit()
        cursor.close()

    if state == "-1":
        query2 = 'Delete from Tag where id = %s and username_taggee = %s and username_tagger = %s'
        cursor2.execute(query2, (cid, username, tagger))
        conn.commit()
        cursor2.close()
    return render_template('confirm.html')

@app.route('/taging', methods=['GET', 'POST'])
def taging():

    taggee = request.form['taggee']
    username = session['username']
    id = request.form['id']

    if taggee == username:
        cursor = conn.cursor()
        sql = 'INSERT into Tag(id,username_tagger,username_taggee,status) VALUES(%s,%s,%s,"1")'
        cursor.execute(sql, (id, username, taggee))
        conn.commit()
        cursor.close()
    else:
       cursor2 = conn.cursor()
       sql2 = "select id, content_name from Content  where id in (select distinct(id) from content  where public = true or id in (select DISTINCT(id) from Member join Share using(group_name) where Member.username = %s)) order by timest DESC"
       cursor2.execute(sql2, taggee)
       data = cursor2.fetchall()
       for line in data:
           if str(id) == str(line[u'id']):
               cursor3 = conn.cursor()
               sql3 ='INSERT into Tag(id,username_tagger,username_taggee,status) VALUES(%s,%s,%s,"0")'
               cursor3.execute(sql3, (id, username, taggee))
               conn.commit()
               cursor3.close()
               return redirect(url_for('home'))
               #return render_template('confirm.html', data=data, taggee=taggee)

       error = "Person cannot be tagged!"
       return render_template('confirm.html', error=error)


    #return redirect(url_for('home'))
    return render_template('confirm.html')

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    comments = request.form['comment']
    username = session['username']
    ids = request.form['id']
    cursor = conn.cursor()
    sql = 'insert into Comment(id, username,comment_text) values( %s, %s, %s)'
    cursor.execute(sql, (ids, username, comments))
    conn.commit()
    cursor.close()

    return redirect(url_for('home'))
    #return render_template('confirm.html', ids=ids, comments=comments, username=username)


@app.route('/unfriendform', methods=['GET', 'POST'])
def unfriendform():
    rname = request.form['username']
    gname = request.form['group']
    creator = session['username']

    cursor = conn.cursor()
    sql = 'Select count(*) as no From member where username =%s and group_name = %s and username_creator = %s'
    cursor.execute(sql, (rname, gname, creator))
    data = cursor.fetchone()
    if str(data['no']) == str(0):
        error_notfriend = 'User is not a member of the group'
        return render_template("confirm.html", error_notfriend=error_notfriend)

    else:
        cursor2 = conn.cursor()
        sql2 = 'Delete from Member where username = %s and group_name = %s and username_creator = %s'


        cursor2.execute(sql2, (rname, gname, creator))
        conn.commit()
        cursor2.close()
        msgblock = "member removed"
        return render_template("confirm.html", msgblock=msgblock)

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')

app.secret_key = 'some key that you will never guess'
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
