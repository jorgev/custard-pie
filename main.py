from flask import Flask, render_template, redirect, request, jsonify
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import ndb
import model
import datetime
import logging

app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def home():
    upcoming = model.Event.query().order(model.Event.start_time).fetch(4)
    return render_template('index.html', upcoming=upcoming)

@app.route('/bios.html', methods=['GET'])
def bios():
    return render_template('bios.html')

@app.route('/upcoming.html', methods=['GET'])
@app.route('/upcoming-shows.html', methods=['GET'])
def upcoming():
    upcoming = model.Event.query().order(model.Event.start_time).fetch()
    cur_month = None
    data = []
    events = []
    for event in upcoming:
        if cur_month != event.start_time.strftime('%B'):
            if cur_month:
                data.append({ 'name': cur_month, 'events': events })
            cur_month = event.start_time.strftime('%B')
            events = []
        events.append(event)
    if events:
        data.append({ 'name': cur_month, 'events': events })
    return render_template('upcoming.html', upcoming=data)

@app.route('/songlist.html', methods=['GET'])
def songlist():
    return render_template('songlist.html')

@app.route('/media.html', methods=['GET'])
def media():
    return render_template('media.html')

@app.route('/news.html', methods=['GET'])
def news():
    news = model.News.query().order(model.News.created).fetch(5)
    return render_template('news.html', news=news)

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        body = request.form['body']
        message = mail.EmailMessage(sender="Web Form <contact@custard-pie.appspotmail.com>",
                to="Custard Pie <custardpieband@gmail.com>",
                subject=subject,
                body=body,
                reply_to="%s <%s>" % (name, email))
        message.send()
        return redirect('/submitted.html')
    return render_template('contact.html')

@app.route('/submitted.html', methods=['GET'])
def submitted():
    return render_template('submitted.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        venue = request.form['venue']
        location = request.form['location']
        start_time = datetime.datetime.strptime('%s %s' % (request.form['date'], request.form['time']), '%Y-%m-%d %H:%M')
        user = users.get_current_user()
        event = model.Event(venue=venue, location=location, start_time=start_time, created_by=user)
        added = event.put()
        return redirect('/admin')
    elif request.args.get('delete'):
        k = ndb.Key(urlsafe=request.args['delete'])
        k.delete()
        return redirect('/admin')
    news = model.News.query().order(model.News.created).fetch()
    upcoming = model.Event.query().order(model.Event.start_time).fetch()
    return render_template('admin.html', upcoming=upcoming, news = news)

@app.route('/events', methods=['GET'])
def events():
    events = []
    limit = 20
    if request.args.get('limit'):
        limit = int(request.args['limit'])
    if request.args.get('venue'):
        venue = request.args['venue']
        event = model.Event.query(model.Event.venue == venue).order(model.Event.start_time).get()
        if event:
            events.append({ 'venue': event.venue, 'location': event.location, 'date': datetime.datetime.strftime(event.start_time, '%A, %B %-d at %-I:%M %p') })
    else:
        upcoming = model.Event.query().order(model.Event.start_time).fetch(limit)
        for event in upcoming:
            events.append({ 'venue': event.venue, 'location': event.location, 'date': datetime.datetime.strftime(event.start_time, '%A, %B %-d at %-I:%M %p') })
    return jsonify(events)

@app.route('/edit_event', methods=['GET', 'POST'])
def edit_event():
    k = ndb.Key(urlsafe=request.args['id'])
    event = k.get()
    if request.method == 'POST':
        event.venue = request.form['venue']
        event.location = request.form['location']
        event.start_time = datetime.datetime.strptime('%s %s' % (request.form['date'], request.form['time']), '%Y-%m-%d %H:%M')
        event.updated_by = users.get_current_user()
        event.put()
        return redirect('/admin')
    return render_template('edit_event.html', event=event)

@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    if request.method == 'POST':
        return redirect('/admin')
    return render_template('add_news.html')

@app.route('/cleanup', methods=['GET'])
def cleanup():
    old = model.Event.query(model.Event.start_time < datetime.start_time.today()).order(model.Event.start_time).fetch()
    for e in old:
        e.key.delete()
    status = { 'entries_deleted': len(old) }
    logging.info('%d event(s) deleted' % len(old))
    return jsonify(status)
