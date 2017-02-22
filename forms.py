from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required, Email


class InsightForm(FlaskForm):
    athlete_id = IntegerField(u'Athlete ID Number', default=153604)
    # year = SelectField(u'Open Year', choices=[(2017, '2017'), (2016, '2016'), (2015, '2015'), (2014, '2014')],
    #                    coerce=int)
    # division = SelectField(u'Division', choices=[(1, 1), (0, 2)], coerce=int)


class RecordForm(FlaskForm):
    # user_id = IntegerField(u'User ID')
    event_date = StringField(u'Event date', validators=[Required()])
    record_type = StringField(u'Record type')
    sport = StringField(u'Sport')
    record = FloatField(u'Record value', validators=[Required()])
    record_unit = StringField(u'Record unit')
    evidence = StringField(u'Evidence')

    # ['user_id', 'create_date', 'event_date', 'record_type', 'sport', 'record_unit', 'record', 'evidence']

    # submit = SubmitField(u'Record')
