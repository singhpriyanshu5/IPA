from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Interviewee, InterviewRegister, InterviewDepartment, InterviewGroup
from django.core.validators import EmailValidator, RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

class InterviewGroupSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='name')

    class Meta:
        model = InterviewGroup
        fields = ('id', 'name', 'url')


class InterviewRegistrationSerializer(serializers.ModelSerializer):
    queueNumber = serializers.SerializerMethodField('cari_queue')
    group = serializers.CharField(source='department.group.name', read_only=True)
    url = serializers.CharField(source='pk', read_only=True)

    class Meta:
        model = InterviewRegister
        fields = ('id', 'group', 'department', 'queueNumber', 'url')

    def cari_queue(self, obj):
        cnt = 0
        for q in InterviewRegister.objects.filter(department=obj.department, status=0).order_by('queueNumber'):
            if q.interviewee.pk == obj.interviewee.pk:
                return 'There are ' + str(cnt) + ' people in front of you'
            else:
                cnt += 1
        return 'There are ' + str(cnt) + ' people in front of you'

    def __init__(self, *args, **kwargs):
        super(InterviewRegistrationSerializer, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = InterviewDepartment.objects.exclude(group__closeSelection=1)

    def validate_department(self, value):
        q = self.context['request'].user
        dept = InterviewDepartment.objects.get(pk=self.initial_data['department'])
        try:
            q.interviewee.interviewRegister.get(department=value)
        except InterviewRegister.DoesNotExist:
            #TODO need to limit number of Queue?
            # if len(q.interviewee.interviewRegister.filter(department__group=dept.group, status = 0)) == 1:
            #     raise serializers.ValidationError('only 1 queue is allowed at a time')
            if dept.group.maxRegister == 0:
                raise serializers.ValidationError("Sorry, queue registration reopens at 8th September 5pm.")
            if len(q.interviewee.interviewRegister.filter(department__group=dept.group)) < dept.group.maxRegister:
                return value
            else:
                raise serializers.ValidationError('you exceeded the number of maximum registration allowed')
        raise serializers.ValidationError('you already registered to this department before')

    def create(self, validated_data):
        q = self.context['request'].user
        validated_data['interviewee'] = q.interviewee
        validated_data['queueNumber'] = validated_data['department'].queueLast + 1
        validated_data['status'] = 0
        validated_data['department'].queueLast += 1
        validated_data['department'].save()
        return super(InterviewRegistrationSerializer, self).create(validated_data)


class InterviewRegistrationSerializer2(serializers.ModelSerializer):
    queueNumber = serializers.SerializerMethodField('cari_queue')
    # registerLeft = serializers.SerializerMethodField('checkLeft')
    department = serializers.CharField(source='department.name')
    group = serializers.CharField(source='department.group.name', read_only=True)
    url = serializers.CharField(source='pk', read_only=True)

    def checkLeft(self, obj):
        return '{0}/{1}'.format(str(obj.department.group.maxRegister - len(obj.interviewee.interviewRegister.all())), str(obj.department.group.maxRegister))

    class Meta:
        model = InterviewRegister
        fields = ('id', 'group', 'department', 'queueNumber', 'url')

    def cari_queue(self, obj):
        cnt = 0
        for q in InterviewRegister.objects.filter(department=obj.department, status=0).order_by('queueNumber'):
            if q.interviewee.pk == obj.interviewee.pk:
                return 'There are ' + str(cnt) + ' people in front of you'
            else:
                cnt += 1
        return 'There are ' + str(cnt) + ' people in front of you'


class InterviewMainSerializer(serializers.ModelSerializer):
    queue = serializers.CharField(source='queueNumber')

    class Meta:
        model = InterviewRegister
        fields = ('id','queue',
                  #'status',
                  'customAnswer', 'comment', 'score')
        #exclude = ( 'queue', 'status',)

class InterviewCallSerializer(serializers.ModelSerializer):
    queue_number = serializers.CharField(source='queueNumber')
    matric = serializers.CharField(source='interviewee.matricNumber')
    name = serializers.CharField(source='interviewee.name')

    class Meta:
        model = InterviewRegister
        fields = ('id', 'queue_number', 'matric', 'name', 'status')


class InterviewResultSerializer(serializers.ModelSerializer):
    matric = serializers.CharField(source='matricNumber')
    accepted = serializers.SerializerMethodField('generateaccepted')

    def generateaccepted(self, obj):
        ret = []
        for q in obj.interviewRegister.filter(resultPending=1).order_by('department'):
            ret.append(q)
        return ret

    class Meta:
        model = Interviewee
        fields = ('id', 'name', 'matric', 'accepted')


class InterviewJudgeSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='id')
    queue = serializers.CharField(source='queueNumber')
    matric = serializers.CharField(source='interviewee.matricNumber')
    name = serializers.CharField(source='interviewee.name')
    result = serializers.SerializerMethodField()

    def get_result(self, obj):
        if obj.resultPending == 0:
            return 'Pending'
        else:
            return 'Accept'

    class Meta:
        model = InterviewRegister
        fields = ('id', 'queue', 'matric', 'name', 'status', 'customAnswer', 'comment', 'score', 'result', 'url')


class InterviewHomeSerializer(serializers.ModelSerializer):
    queue = serializers.SerializerMethodField('cari_queue')
    department = serializers.CharField(source='department.name')
    group = serializers.CharField(source='department.group')
    def cari_queue(self, obj):
        cnt = 0
        for q in InterviewRegister.objects.filter(department=obj.department, status=0).order_by('queueNumber'):
            if q.interviewee.pk == obj.interviewee.pk:
                return 'There are ' + str(cnt) + ' people in front of you'
            else:
                cnt += 1
        return 'There are ' + str(cnt) + ' people in front of you'

    class Meta:
        model = InterviewRegister
        fields = ('group', 'department', 'queue')


class InterviewAdminSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source='id')
    matric = serializers.CharField(source='interviewee.matricNumber')
    name = serializers.CharField(source='interviewee.name')

    class Meta:
        model = InterviewRegister
        fields = ('id', 'matric', 'name', 'url')


class IntervieweeRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.CharField (
        source='user.username',
        style={'placeholder': 'btp@e.ntu.edu.sg'.lower()},
        validators=[EmailValidator()],
    )
    password = serializers.CharField (
        source='user.password', 
        write_only=True, 
        allow_blank=True, 
        style={'placeholder': 'Final Fantasy', 'input_type': 'password'},
    )
    name = serializers.CharField (
        style={'placeholder': 'Donald Trump'},
        validators=[RegexValidator('^[A-Za-z ]+$', 'Enter a valid name.')],
    )
    matric_number = serializers.CharField (
        style={'placeholder': 'U1234567A'},
        validators=[RegexValidator('^[A-Z][0-9]{7}[A-Z]$', 'Enter a valid matric number.')],
    )
    year = serializers.IntegerField (
        style={'placeholder': 4},
        validators=[MinValueValidator(1, 'Enter a valid year of study'), MaxValueValidator(8, 'Enter a valid year of study')],
    )
    major = serializers.CharField (
        style={'placeholder': 'Mathematical Science'},
    )
    phone = serializers.CharField (
        style={'placeholder': '12345678'},
        validators=[RegexValidator('^\+?[-0-9 ]{6,20}$', 'Enter a valid phone number')],
    )
    hall = serializers.CharField (
        style={'placeholder': 'Binjai Hall'},
    )
    other_ECA = serializers.CharField (
        style={'placeholder': 'SCSE Club, CEE Club, ...'},
        required=False
    )
    exchange_this_semester = serializers.BooleanField (
      
    )

    class Meta:
        model = Interviewee
        fields = (
            'id', 'email', 'password', 'name', 'matric_number', 'year', 
            'major', 'phone', 'hall', 'other_ECA', 'exchange_this_semester',
        )

    def is_valid(self, raise_exception=False):
        self.initial_data['email'] = self.initial_data['email'].lower()
        error = super(IntervieweeRegistrationSerializer, self).is_valid(raise_exception = raise_exception)

        try:
            User.objects.get(username=self.initial_data['email'])
            self._errors['email'] = ['This email is already registered']
            error = False
        except:
            pass

        try:
            Interviewee.objects.get(matricNumber=self.initial_data['matric_number'])
            if not ('matric_number' in self._errors):
                self._errors['matric_number'] = ['This matric number is already registered']
        except:
            return error

        return False

    def update(self, instance, validated_data):
        global q
        if instance is not None:
            q = validated_data.pop('user', None)
            q.pop('username', None)
        interviewee = super(IntervieweeRegistrationSerializer, self).update(instance, validated_data)
        if 'password' in q and q['password']:
            interviewee.user.set_password(q['password'])
            interviewee.user.save()
        return interviewee

    def create(self, validated_data):
        info = validated_data.pop('user')
        try:
            user = User.objects.create_user(username=info.get('username'), password=info.get('password'))
        except:
            raise serializers.ValidationError('user already exists')
        validated_data['user'] = user
        return super(IntervieweeRegistrationSerializer, self).create(validated_data)


class IntervieweeRegistrationUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(source='user.password', write_only=True, allow_blank=True, style={'placeholder': 'Password1', 'input_type': 'password'},)

    class Meta:
        model = Interviewee
        fields = ('id', 'password', 'name', 'matricNumber', 'year', 'major', 'phone')

    def update(self, instance, validated_data):
        global q
        if instance is not None:
            q = validated_data.pop('user', None)
            q.pop('username', None)
        interviewee = super(IntervieweeRegistrationUpdateSerializer, self).update(instance, validated_data)
        if ('password' in q) and q['password']:
            interviewee.user.set_password(q['password'])
            interviewee.user.save()
        return interviewee

    def create(self, validated_data):
        info = validated_data.pop('user')
        try:
            user = User.objects.create_user(username=info.get('username'), password=info.get('password'))
        except:
            raise serializers.ValidationError('user already exists')
        validated_data['user'] = user
        return super(IntervieweeRegistrationUpdateSerializer, self).create(validated_data)

