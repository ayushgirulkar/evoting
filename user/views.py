from MySQLdb import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import render
import mysql.connector as sql
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import render, redirect
from django.contrib.auth.models import User  # For password hashing
import random
import smtplib
from voter_admin import models
from .blockchain import*
from django.http import StreamingHttpResponse, HttpResponseServerError
from django.shortcuts import render
from .livestream import LiveStream
from django.db.models import Count
from voter_admin.models import*
from django.db.models import Max
live_stream = LiveStream()
#redirection links voter
def voter_reg(request):
    current_phase = VotePhase.objects.get(pk=1).phase  # Assuming only one VotePhase object
    user = Voter.objects.get(email=request.session.get('user_email'))
    is_registered = user.is_registered
    try:
        with open('election_title.txt', 'r') as file:
            title = file.read()
    except FileNotFoundError:
        title = "No title available"
    print(is_registered)
    context = {'current_phase': current_phase, 'is_registered':is_registered,'title':title+" Election"}
    print("current: ",current_phase)
    return render(request,'voter/voter_register.html',context)

def voter_menu(request):
    email = request.session.get('user_email')
    print("EMAIL = ",email)
    user = Voter.objects.get(email=email).name
    print("USER = ",user)
    return render(request,'voter/voter_menu.html',{'voter':user})

def voter_voting(request):
    try:
        with open('election_title.txt', 'r') as file:
            title = file.read()
    except FileNotFoundError:
        title = "No title available"

    # check if user can vote or not
    can_vote = Voter.objects.get(email=request.session.get('user_email')).has_voted

    # get current phase of voting
    candidates = Candidate.objects.all()
    current_phase = VotePhase.objects.get(pk=1).phase  # Assuming only one VotePhase object

    # get voter is registered or not
    voter = Voter.objects.get(email=request.session.get('user_email'))  # Adjust this based on your actual user model and authentication mechanism
    is_registered = voter.is_registered
    voter_id = voter.voter_id


    context = {
        'current_phase': current_phase,
        'candidates': candidates,
        'election_title': title + " Election",
        'is_registered': is_registered,
        'can_vote': can_vote,
        'voter_id':voter_id
    }
    print(context)
    return render(request, 'voter/voter_voting.html', context)

def voter_signup(request):
    return render(request,'voter/signup.html')

def voter_result(request):
    result_status = ElectionResultStatus.objects.first()
    has_declared = result_status.result_declared if result_status else False

    if has_declared:
        candidate_with_highest_votes = Candidate.objects.aggregate(max_votes=Max('votes'))
        winner = Candidate.objects.get(votes=candidate_with_highest_votes['max_votes'])
        return render(request, 'voter/voter_result.html', {'has_declared': has_declared, 'winner': winner})
    else:
        return render(request, 'voter/voter_result.html', {'has_declared': has_declared})


def count_votes_per_candidate(request):
    # Count the number of votes for each distinct candidate
    votes_per_candidate = Block.objects.values('encrypted_candidate_id').annotate(vote_count=Count('encrypted_candidate_id'))
    print(votes_per_candidate)
    # Prepare the data to be sent as JSON response
    data = []
    for candidate in votes_per_candidate:
        candidate_id = candidate['encrypted_candidate_id']
        vote_count = candidate['vote_count']
        data.append({'candidate_id': candidate_id, 'vote_count': vote_count})

    return render(request,"index.html")

def voter_login(request):
    return render(request,'voter/voter_login.html')



def voter_login_view(request):
    if request.method=="POST":
        m=sql.connect(host="localhost",user="root",passwd="123",database='election_db')
        cursor=m.cursor()

        _email = request.POST.get('email')
        _pass = request.POST.get('password')
        
        c="select password from voter_admin_voter where email='{}'".format(_email)
        cursor.execute(c)

        hashed_password = cursor.fetchone()
        print(hashed_password)

        if not hashed_password:
            print("User does not exist")
            error_message = 'Invalid username or password'  # Handle potential errors
            return render(request, "voter/voter_login.html")
        else:
            hashed_password = hashed_password[0]  # Extracting the hashed password from the tuple
            
            # Step 3: Verify the password
            if check_password(_pass,hashed_password):
                print("Login successful")
                request.session['user_email'] = _email
                request.session['voter_id'] = Voter.objects.get(email=_email).voter_id
                return redirect('voter_menu')
            else:
                print("Incorrect password")
                error_message = 'Invalid username or password'  # Handle potential errors
                return render(request, "voter/voter_login.html")

    context = { 'error_message': error_message if error_message else None}
    return render(request, 'voter/voter_login.html', context)


def signup_session(request):
    if request.method == 'POST':
        # Store form data in session
        _password = request.POST.get('password')
        _confirm_password = request.POST.get('confirm_password')

        # Validate password match
        if _password != _confirm_password:
            return render(request, 'voter/signup.html', {'error': 'Passwords do not match'})

        request.session['name'] = request.POST.get('name')
        request.session['address'] = request.POST.get('address')
        request.session['mobile'] = request.POST.get('mobile')
        request.session['dob'] = request.POST.get('dob')
        request.session['password'] = request.POST.get('password')
        request.session['confirm_password'] = request.POST.get('confirm_password')
        return render(request, 'voter/otp_signup/email_input.html')

def email_verify(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = generate_otp()
        print('Email Verify')
        request.session['otp'] = otp
        request.session['email'] = email
        # Send OTP via email
        send_mail(
            'OTP Verification',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        print("OTP sentt")

        messages.success(request, 'An OTP has been sent to your email.')

    return render(request, 'voter/otp_signup/email_verify.html')

def verify_signup(request):
    if 'otp' not in request.session or 'email' not in request.session:
        return redirect('index')

    if request.method == 'POST':
        user_otp = request.POST['otp']
        if user_otp == request.session['otp']:

            _name = request.session.get('name')
            _address = request.session.get('address')
            _email = request.session.get('email')
            _mobile = request.session.get('mobile')
            _dob = request.session.get('dob')
            _password = request.session.get('password')

            try:
                hashed_password = make_password(_password)

                voter = Voter(
                    address=_address,
                    name=_name,
                    email=_email,
                    mobile=_mobile,
                    dob=_dob,
                    password=hashed_password
                )

                voter.save()
                return render(request, 'voter/voter_login.html', {'success': 'Voter registered successfully'})
            except IntegrityError as e:
                print(e)
                return render(request, 'voter/signup.html', {'error': str(e)})

        else:
            error = "INVALID OTP..."
            return render(request, 'voter/otp_signup/email_verify.html',{'error':error})

    return render(request, 'voter/otp_signup/email_verify.html')



def signup_view(request):
    if request.method == 'POST':
        _name = request.POST.get('name')
        _address = request.POST.get('address')
        _email = request.POST.get('email')
        _mobile = request.POST.get('mobile')
        _dob = request.POST.get('dob')
        _password = request.POST.get('password')
        _confirm_password = request.POST.get('confirm_password')

        # Validate password match
        if _password != _confirm_password:
            return render(request, 'voter/signup.html', {'error': 'Passwords do not match'})
        
        try:
            hashed_password = make_password(_password)

            voter = Voter(
            address = _address,
            name = _name,
            email = _email,
            mobile = _mobile,
            dob = _dob,
            password = hashed_password
            )

            voter.save()
            # Additional processing (e.g., send confirmation email)
            return render(request, 'voter/voter_login.html', {'success': 'Voter registered successfully'})

        except IntegrityError as e:  # Handle potential database-related errors
            # Check for specific errors (e.g., unique constraint violations)
            # and provide appropriate error messages
            return render(request, 'voter/signup.html', {'error': str(e)})

        except Exception as e:  # Catch other unexpected errors
            return render(request, 'voter/signup.html', {'error': f'An error occurred: {str(e)}'})

    return render(request, 'voter/signup.html')

def vote(request):
    if request.method == 'POST':
        can_vote = Voter.objects.get(email=request.session.get('user_email')).has_voted
        if can_vote:
            # User has already voted, prevent them from voting again
            print("ALREADY VOTED...")
            messages.error(request, "You have already voted.")
            return redirect('voter_menu')

        candidate_id = request.POST.get('candidate_id')
        if not candidate_id:
            print("CANIDATE NOT FOUND...")
            return render(request, 'voter/voter_voting.html', {'error_message': 'Invalid request', 'message': 'Candidate id missing'})

        try:
            candidate = Candidate.objects.get(pk=candidate_id)
            print("THE CANDIDATE ID IN USER = ",candidate_id)
            print("CANDIDATE AVAILABLE :",candidate)
        except Candidate.DoesNotExist:
            return render(request, 'voter/voter_voting.html', {'error_message': 'Invalid request', 'message': 'Invalid Candidate ID'})

        # Add vote to the blockchain
        voter_id = request.POST.get('voter_id')  # Assuming you have voter_id in your form
        print("THE VOTER ID = ",voter_id)
        previous_hash = Block.objects.latest('timestamp').block_hash if Block.objects.exists() else None
        # filename = "encryption_key.dat"
        # with open(filename, "rb") as key_file:
        #     demo_key = key_file.read()
        cipher_suite = read_key_from_file()
        print(cipher_suite)
        block = create_block(voter_id, candidate_id, previous_hash, cipher_suite)

        # Save the Block object
        block.save()
        print(block)
        print("BLOCK SAVED TO DATABASE")

        # set has voted true in the databse
        request.session['has_voted'] = True
        voter = Voter.objects.get(voter_id=voter_id)
        voter.has_voted = True
        voter.save()

        return render(request, 'voter/voter_voting.html', {'message': 'VOTED SUCCESSFULLY...'})
    else:
        print("DIRECT ELSE BLOCK ...")
        # If the request method is not POST, render the voter_voting template with proper messages
        return render(request, 'voter/voter_voting.html', {'error_message': 'Invalid request method', 'message': 'Invalid request method'})

def generate_otp():
    return str(random.randint(100000, 999999))


def otp_reg(request):
    if request.method == 'POST':
        email = request.session.get('user_email')
        otp = generate_otp()
        request.session['otp'] = otp
        request.session['email'] = email
        print("Hello")
        # Send OTP via email
        send_mail(
            'OTP Verification',
            f'Your OTP is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, 'An OTP has been sent to your email.')
        return redirect('verify_otp')

    return render(request, 'voter/voter_register.html')


def verify_otp(request):
    if 'otp' not in request.session or 'email' not in request.session:
        return redirect('index')

    if request.method == 'POST':
        user_otp = request.POST['otp']
        if user_otp == request.session['otp']:
            user_email = request.session.get('user_email')
            print(user_email)
            voter = Voter.objects.get(email=user_email)
            voter.is_registered = True
            voter.save()
            messages.success(request, 'Voter Registered Successfully..!!')
            return render(request, 'voter/verification_success.html')
        else:
            messages.error(request, 'Invalid OTP, please try again.')
            return redirect('verify_otp')

    return render(request, 'voter/verify_otp.html')

# FACE DETIALS
from django.http import HttpResponseServerError, StreamingHttpResponse
from django.views.decorators import gzip
import cv2

cascade_path = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)
video_capture = cv2.VideoCapture(0)


@gzip.gzip_page
def live_feed(request):
    try:
        return StreamingHttpResponse(recognize_faces(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        print("Error:", e)
        return HttpResponseServerError("Internal Server Error")


# FACIAL NEW DATA
# Create an instance of LiveStream
# Define view to start streaming
def start_stream(request):
    live_stream = LiveStream()
    return live_stream.start_streaming()

# Define view to stop streaming
def stop_stream(request):
    live_stream.stop_streaming()
    return HttpResponse("Streaming stopped")
