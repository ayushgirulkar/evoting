import mysql.connector as sql
from cryptography.fernet import Fernet, InvalidToken
from django.core.checks import messages
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from .forms import CandidateForm, LoginForm
from .models import Voter, Candidate, VotePhase, ElectionResultStatus, EncryptionKey, Block, ElectionResult
from django.utils import timezone
from voter_admin.models import Block
from django.db.models import Max

from .blockchain import decrypt_data, election_generate_key


def login_view(request, error_message=None):
    global em, pwd
    if request.method == "POST":
        m = sql.connect(host="localhost", user="root", passwd="123", database='election_db')
        cursor = m.cursor()
        d = request.POST
        print(d)
        for key, value in d.items():
            if key == "email":
                em = value
            if key == "password":
                pwd = value

        c = "select * from voter_admin_adminprofile where admin_email='{}' and admin_password='{}'".format(em, pwd)
        cursor.execute(c)
        t = tuple(cursor.fetchall())
        print(t)
        if t == ():
            print("not login")
            error_message = 'Invalid username or password'  # Handle potential errors
            return render(request, "login.html")
        else:
            print("login")
            return redirect('admin_menu')
    else:
        form = LoginForm()

    context = {'error_message': error_message if error_message else None}
    return render(request, 'login.html', context)


def add_candidate_db(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        party = request.POST.get('party')
        image = request.FILES.get('image')

        if name and party and image:
            candidate = Candidate(name=name, party=party, image=image)
            candidate.save()
            return render(request, 'admin/admin_add_candidate.html',
                          {'success': 'Candidate Added Succesfully...'})  # Success page
    else:
        form = CandidateForm()
    return render(request, 'admin/admin_add_candidate.html')


def delete_candidate(request):
    if request.method == 'POST':
        success = ""
        error = ""
        candidate_id = request.POST.get('candidate_id')
        print(candidate_id)
        try:
            candidate = Candidate.objects.get(candidate_id=candidate_id)
            candidate.delete()
            success = "Candidate successfully deleted."
        except Candidate.DoesNotExist:
            error = "Candidate not found..."
    context = {'error': error, 'success': success, 'candidates': Candidate.objects.all()}
    return render(request, "admin/admin_details.html", context)


def block_records(request):
    blocks = Block.objects.all()
    return render(request, 'admin/block_records.html', {'blocks': blocks})


def change_vote_phase(request):
    if request.method == 'POST':
        # Get the selected phase from the form
        selected_phase = request.POST.get('phase')

        # Check if valid option is selected
        if selected_phase in ['registration', 'voting', 'closed']:
            # Check if there are at least 2 candidates
            if Candidate.objects.count() < 2 and selected_phase == 'voting':
                return render(request, "admin/admin_phase.html", {
                    'error': 'At least 2 candidates are required to change the phase to voting.'})  # Assuming 'change_vote_phase' is the name of the view

            # Update the VotePhase object with the new phase
            vote_phase, created = VotePhase.objects.get_or_create(pk=1)  # Assuming only one VotePhase object
            vote_phase.phase = selected_phase
            vote_phase.save()

            current_phase = selected_phase
            # Success message
            message = f"Vote phase successfully changed to {selected_phase}."
        else:
            # Error message for invalid selection
            message = "Invalid phase selected. Please choose a valid option."
    else:
        # Get the current phase
        current_phase = VotePhase.objects.get(pk=1).phase  # Assuming only one VotePhase object
        message = ''  # Empty message for initial load

    # Prepare context for template
    context = {'current_phase': current_phase, 'message': message}
    return render(request, 'admin/admin_phase.html', context)


def login(request):
    return render(request, 'login.html')


def logout(request):
    return render(request, "index.html")


# redirection urls admin

def admin_menu(request):
    total_candidates = Candidate.objects.count()
    total_voters = Voter.objects.count()
    total_blocks = Block.objects.count()-1
    registered_voters_count = Voter.objects.filter(is_registered=True).count()
    result_status = ElectionResultStatus.objects.first()
    has_declared = result_status.result_declared if result_status else False
    # total_voters_voted = Block.objects.values('encrypted_voter_id').distinct().count()

    context = {
        'total_candidates': total_candidates,
        'total_voters': total_voters,
        'registered_voters_count': registered_voters_count,
        'has_declared': has_declared,
        'total_blocks':total_blocks
        # 'total_voters_voted': total_voters_voted,
    }
    print(context)
    return render(request, 'admin/admin_menu.html', context)


def admin_detail(request):
    candidates = Candidate.objects.all()  # Retrieve all candidates

    context = {
        'candidates': candidates,
    }

    return render(request, 'admin/admin_details.html', context)


def admin_change(request):
    current_phase = VotePhase.objects.get(pk=1).phase  # Assuming only one VotePhase object
    context = {'current_phase': current_phase}

    return render(request, 'admin/admin_phase.html', context)


def add_candidate(request):
    return render(request, 'admin/admin_add_candidate.html')


def count_votes(request):
    # try:
    # Create a dictionary to map candidate IDs to candidate
    candidates = {candidate.candidate_id: candidate for candidate in Candidate.objects.all()}

    # Iterate over the keys and print their types
    for key in candidates.keys():
        print(f"Key: {key}, Type: {type(key)}")

    # Iterate over all Block objects
    blocks = Block.objects.all().values_list('encrypted_candidate_id', flat=True)[1:]
    print(blocks)

    for encrypted_candidate_id in blocks:
        print("ENCRYPTED CANDIDATE ID = ", encrypted_candidate_id)
        decrypted_data = int(decrypt_data(encrypted_candidate_id))
        print("Decrypted data without decode:", type(decrypted_data))
        if decrypted_data in candidates:
            # Increment the vote count for the candidate
            candidate_id = decrypted_data
            print("candidates[candidate_id] = ", candidates[candidate_id])
            candidate = candidates[candidate_id]
            candidate.votes += 1
            candidate.save()
            print("Vote count incremented for candidate ID:", candidate_id)
        else:
            print("Candidate not found for decrypted data:", decrypted_data)

    result_status = ElectionResultStatus.objects.get()
    print(result_status)
    result_status.result_calculated = True
    result_status.save()

    return redirect('admin_result_render')


def admin_result_render(request):
    result = ElectionResultStatus.objects.first()

    winner=""
    if result.result_calculated:
        candidate_with_highest_votes = Candidate.objects.aggregate(max_votes=Max('votes'))
        winner = Candidate.objects.get(votes=candidate_with_highest_votes['max_votes']).name

    context = {
        'has_declared': result.result_declared,
        'has_calculated': result.result_calculated,
        'vote_phase': VotePhase.objects.get(pk=1).phase,
        'candidates': Candidate.objects.all().order_by('-votes'),
        'winner':winner
    }
    print("RESULT  = ",context)
    return render(request, 'admin/admin_result.html', context)


def declare_result(request):
    # Get or create the ElectionResultStatus instance
    result_status = ElectionResultStatus.objects.get()
    result_status.result_declared = True
    result_status.save()

    # Getting the election title
    try:
        with open('election_title.txt', 'r') as file:
            election_name = file.read()
    except FileNotFoundError:
        election_name = "No title available"

    # Save result to ElectionResult model
    winner = Candidate.objects.all().order_by('-votes')
    candidate_with_highest_votes = Candidate.objects.aggregate(max_votes=Max('votes'))
    highest_voted_candidate = Candidate.objects.get(votes=candidate_with_highest_votes['max_votes'])

    if election_name and highest_voted_candidate:
        ElectionResult.objects.create(
            election_name=election_name,
            candidate_name=highest_voted_candidate.name,
            total_votes=highest_voted_candidate.votes,
            result_declaration_date=timezone.now()
        )

    return redirect('admin_result_render')


def change_key_render(request):
    return render(request, "admin/admin_key.html")


def change_key(request):
    election_generate_key()
    return render(request, "admin/admin_key.html", {'message': 'Key Changed...'})


def admin_title_render(request):
    return render(request, 'admin/admin_edit_title.html')


def save_election_title(request):
    message = None
    if request.method == 'POST':
        title = request.POST.get('election_title', '')
        with open('election_title.txt', 'w') as file:
            file.write(title)
        message = "Election title saved successfully."
    return render(request, 'admin/admin_edit_title.html', {'message': message})


from django.shortcuts import render
from .models import Block


def block_list(request):
    blocks = Block.objects.all()
    candidate_ids = [block.encrypted_candidate_id for block in blocks]
    return render(request, 'admin/sample.html', {'candidate_ids': candidate_ids})


def new_election(request):
    # Truncate (delete all records) from each table
    # make voters has not voted and not registered yet
    voters_to_reset = Voter.objects.filter(has_voted=True) | Voter.objects.filter(is_registered=True)
    voters_to_reset.update(has_voted=False, is_registered=False)

    Candidate.objects.all().delete()
    Block.objects.all().delete()
    ElectionResultStatus.objects.all().delete()
    VotePhase.objects.all().delete()

    Block.objects.create(
        encrypted_voter_id=b'encrypted_voter_id_value',
        encrypted_candidate_id=b'encrypted_candidate_id_value',
        timestamp='2024-03-17 12:00:00',  # Assuming timestamp is a valid datetime string
        previous_hash=b'previous_hash_value',
        block_hash=b'block_hash_value'
    )

    result_status = ElectionResultStatus.objects.create(result_declared=False,result_calculated=False)
    vote_phase = VotePhase.objects.get_or_create(pk=1, defaults={'phase': 'registration'})

    # Optionally, you can return a response indicating the tables have been truncated
    return render(request, "admin/admin_edit_title.html", {'message': 'New Election Enter Election Title ...'})
