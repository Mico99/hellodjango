import os
from io import BytesIO
import xlwt

from django.contrib.admin.utils import quote
from django.db.models import Avg
from django.http import JsonResponse, HttpResponse, HttpRequest, StreamingHttpResponse
from django.shortcuts import render, redirect

from vote.captcha import Captcha
from vote.utils import generate_captcha_code, generate_mobile_code
from vote.forms import LoginForm, RegisterForm
from vote.models import Subject, Teacher, User


# Create your views here.

def login(request):

    """登录"""
    hint = ''
    backurl = request.GET.get('backurl', '/')
    if request.method == 'POST':
        backurl = request.POST['backurl']
        form = LoginForm(request.POST)
        if form.is_valid():
            #对验证码进行验证
            code_from_session = request.session.get('captcha_code')
            code_from_user = form.cleaned_data['code']
            if code_from_session.lower() == code_from_user.lower():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = User.objects.filter(username=username, password=password).first()
                if user:
                    #登录成功后将用户编号和用户名保存在session中
                    request.session['userid'] = user.no
                    request.session['username'] = user.username
                    return redirect('/subjects/')
                else:
                    hint = '用户名或密码错误'
        else:
            hint = '请输入有效的登录信息'
    return render(request, 'login.html', {'hint': hint, 'backurl':backurl})


def register(request):
    page, hint = 'register.html', ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            page = 'login.html'
            hint = '注册成功，请登录'
        else:
            hint = '请输入有效的注册信息'
    return render(request, page, {'hint': hint})


def get_captcha(request):
    """生成图片验证码"""
    code = generate_captcha_code()
    request.session['captcha_code'] = code
    image_data = Captcha.instance().generate(code, fmt='PNG')
    return HttpResponse(image_data, content_type='image/png')


def logout(request):
    """注销"""
    request.session.flush()
    return redirect('/')


def show_subjects(request):
    """查看所有学科"""
    subjects = Subject.objects.all()
    return render(request, 'subject.html', {'subjects': subjects})


def show_teachers(request):
    """显示指定学科的老师"""
    try:
        sno = int(request.GET['sno'])
        subject = Subject.objects.get(no=sno)
        teachers = subject.teacher_set.all()
        return render(request, 'teachers.html', {'subject': subject, 'teachers': teachers})
    except (KeyError, ValueError, Subject.DoesNotExist):
        return redirect('/')


def praise_or_criticize(request: HttpRequest):
    """投票"""
    if 'username' in request.session:
        try:
            tno = int(request.GET['tno'])
            teacher = Teacher.objects.get(no=tno)
            if request.path.startswith('/praise'):
                teacher.good_count += 1
            else:
                teacher.bad_count += 1
            teacher.save()
            data = {'code': 200, 'message': '操作成功'}
        except(KeyError, ValueError, Teacher.DoseNotExist):
            data = {'code': 404, 'message': '操作失败'}
    else:
        data = {'code': 401, 'message':'请先登录'}
    return JsonResponse(data)


def show_teachers_data(request):
    """查看所有老师数据"""
    return render(request, 'bar2.html')


def export_pdf(request):
    """导出PDF文档"""
    path = os.path.dirname(__file__)
    filename = os.path.join(path, 'resources/Python全栈+人工智能.pdf')
    file_stream = open(filename, 'rb')
    file_iter = iter(lambda: file_stream.read(1024), b'')
    resp = StreamingHttpResponse(file_iter, content_type='application/pdf')
    filename = quote('Python全栈+人工智能.pdf')
    resp['content-disposition'] = f'inline; filename="{filename}"'
    return resp


def export_teachers_excel(request):
    wb = xlwt.Workbook()
    sheet = wb.add_sheet('老师信息表')
    queryset = Teacher.objects.all().select_related('subject')
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    props = ('name', 'detail', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, Subject):
                value = value.name
            sheet.write(row + 1, col, value)
    buffer = BytesIO()
    wb.save(buffer)
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    filename = quote('老师.xls')
    resp['content-disposition'] = f'attachment; filename="{filename}"'
    return resp


def show_bar(request, no):
    """显示柱状图"""
    return render(request, f'bar{no}.html')


def get_subjects_data(request):
    queryset = Teacher.objects.values('subject__name').annotate(
        good=Avg('good_count'), bad=Avg('bad_count'))
    names = [result['subject__name'] for result in queryset]
    good = [result['good'] for result in queryset]
    bad = [result['bad'] for result in queryset]
    return JsonResponse({'names': names, 'good': good, 'bad': bad})


def get_teachers_data(request):
    # 查询所有老师的信息(注意：这个地方稍后也需要优化)
    queryset = Teacher.objects.all()
    # 用生成式将老师的名字放在一个列表中
    names = [teacher.name for teacher in queryset]
    # 用生成式将老师的好评数放在一个列表中
    good = [teacher.good_count for teacher in queryset]
    # 用生成式将老师的差评数放在一个列表中
    bad = [teacher.bad_count for teacher in queryset]
    # 返回JSON格式的数据
    return JsonResponse({'names': names, 'good': good, 'bad': bad})