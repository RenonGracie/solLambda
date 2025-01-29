import datetime
from time import sleep
from utils.intakeq_bot.const import *
from utils.settings import settings
from utils.typeform_utils import *
from utils.intakeq_bot.web import Web

web: Web | None = None

def __bot(data: TypeformData, first_name: str = None, last_name: str = None):
    global web
    web = Web()

    web.get(settings.INTAKEQ_SIGNUP_FORM)

    # First Name + Last Name
    web.input_value(f"{first_name} {last_name}", Xpath.Input.id("Name"))
    # Email
    web.input_value(data.get_value(TypeformIds.EMAIL), Xpath.Input.id("Email"))

    # ===============================
    web.click(Xpath.Button.submit)
    # ===============================
    sleep(1)

    try:
        # 1. Please state your university and (anticipated or past) graduation year.
        web.input_value(data.get_value(TypeformIds.UNIVERSITY), Xpath.Input.graduation_year)
    except Exception:
        web.click("//button[@type='submit' and contains(text(),'New Intake')]")
        sleep(1)

        # 1. Please state your university and (anticipated or past) graduation year.
        web.input_value(data.get_value(TypeformIds.UNIVERSITY), Xpath.Input.graduation_year)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    def __multiple_elements(values: list):
        for val in values:
            if web.elements(Xpath.Input.label_complete(val)):
                web.click(Xpath.Input.label_complete(val))
            else:
                web.click(Xpath.Input.label(val))
        # ===============================
        web.click(Xpath.Button.next_page)
        # ===============================
        sleep(1)

    def __single_elements(single_value):
        if web.elements(single_value):
            web.click(Xpath.Input.label_complete(data.get_value(TypeformIds.DRUGS)))
        else:
            web.click(Xpath.Input.label(data.get_value(TypeformIds.DRUGS)))

        # ===============================
        web.click(Xpath.Button.next_page)
        # ===============================
        sleep(1)

    def __radio_element_click(radio_value, index):
        web.click(Xpath.Input.table_radio(radio_value, index))

    # 2. I would like a therapist that:
    __multiple_elements(data.get_value(TypeformIds.I_WOULD_LIKE_THERAPIST))

    # 3. Are there any lived experiences you identify with that you feel are important to your match?
    __multiple_elements(data.get_value(TypeformIds.LIVED_EXPERIENCES))

    # 4. Do you drink alcohol? If yes, how often per week?
    __single_elements(data.get_value(TypeformIds.ALCOHOL))

    # 5. Do you use recreational drugs? If yes, how often per week?
    __single_elements(data.get_value(TypeformIds.DRUGS))

    for i in range(1, 10):
        value: str = ""
        if i == 1:
            # 6.1. Little interest or pleasure in doing things
            value = data.get_value(TypeformIds.PLEASURE_DOING_THINGS)
        elif i == 2:
            # 6.2. Feeling down, depressed, or hopeless
            value = data.get_value(TypeformIds.FEELING_DOWN)
        elif i == 3:
            # 6.3. Trouble falling or staying asleep, or sleeping too much
            value = data.get_value(TypeformIds.TROUBLE_FALLING)
        elif i == 4:
            # 6.4. Feeling tired or having little energy
            value = data.get_value(TypeformIds.FEELING_TIRED)
        elif i == 5:
            # 6.5. Poor appetite or overeating
            value = data.get_value(TypeformIds.POOR_APPETITE)
        elif i == 6:
            # 6.6. Feeling bad about yourself - or that you are a failure or have let yourself or your family down
            value = data.get_value(TypeformIds.FEELING_BAD_ABOUT_YOURSELF)
        elif i == 7:
            # 6.7. Trouble concentrating on things, such as reading the newspaper or watching television
            value = data.get_value(TypeformIds.TROUBLE_CONCENTRATING)
        elif i == 8:
            # 6.8. Moving or speaking so slowly that other people could have noticed. Or the opposite -
            # being so fidgety or restless that you have been moving around a lot more than usual.
            value = data.get_value(TypeformIds.MOVING_OR_SPEAKING_SO_SLOWLY)
        elif i == 9:
            # 6.9. Thoughts that you would be better off dead, or of hurting yourself
            value = data.get_value(TypeformIds.SUICIDAL_THOUGHTS)
        __radio_element_click(value, i)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)


    for i in range(7):
        value: str = ""
        if i == 0:
            # 8.1 Feeling nervous, anxious, or on edge
            value = data.get_value(TypeformIds.FEELING_NERVOUS)
        elif i == 1:
            # 8.2 Not being able to stop or control worrying
            value = data.get_value(TypeformIds.NOT_CONTROL_WORRYING)
        elif i == 2:
            # 8.3 Worrying too much about different things
            value = data.get_value(TypeformIds.WORRYING_TOO_MUCH)
        elif i == 3:
            # 8.4 rouble relaxing
            value = data.get_value(TypeformIds.TROUBLE_RELAXING)
        elif i == 4:
            # 8.5 Being so restless that it is hard to sit still
            value = data.get_value(TypeformIds.BEING_SO_RESTLESS)
        elif i == 5:
            # 8.6 Becoming easily annoyed or irritable
            value = data.get_value(TypeformIds.EASILY_ANNOYED)
        elif i == 6:
            # 8.7 Feeling afraid, as if something awful might happen
            value = data.get_value(TypeformIds.FEELING_AFRAID)
        __radio_element_click(value, i + 1)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # # 9. If you checked off any problems in the previous question,
    # # how difficult have these problems made it for you to do your work,
    # # take care of things at home, or get along with other people?
    # if web.elements(Xpath.Input.label_complete(user[25])):
    #     web.click(Xpath.Input.label_complete(user[25]))
    # else:
    #     web.click(Xpath.Input.label(user[25]))

    # # ===============================
    # web.click(Xpath.button.next_page)
    # # ===============================
    # sleep(1)

    # 10. What brings you to therapy at this time?
    web.input_value(data.get_value(TypeformIds.WHAT_BRINGS_YOU_TO_THERAPY), Xpath.Input.therapy_time)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # 11.3 Age
    web.input_value(data.get_value(TypeformIds.AGE), Xpath.Input.sibling("Age"))

    # 11.4 Gender
    gender = data.get_value(TypeformIds.GENDER)
    if web.elements(Xpath.Input.label_complete(gender)):
        web.click(Xpath.Input.label_complete(gender))
    else:
        web.click(Xpath.Input.label(gender))

    # 11.6 Phone Number
    web.input_value(data.get_value(TypeformIds.PHONE).removeprefix("+1"), Xpath.Input.sibling("Phone Number"))
    web.click(Xpath.Input.sibling("Phone Number"))

    # 11.7 State
    web.select_option(data.get_value(TypeformIds.STATE), Xpath.Input.state)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # 12. What days and times work best for your first session?
    # Please include your time zone.
    # (E.g. Mondays 6-7pm, Thursdays 4-6pm ET)
    # We will use your response to schedule your first therapy session with your designated therapist-in-training. *
    web.input_value(data.get_value(TypeformIds.BEST_TIME_FOR_FIRST_SESSION), "//input[@ng-model='question.Answer']")

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================

    # 13.1. How did you hear about Sol Health?
    for text in data.get_value(TypeformIds.HOW_DID_YOU_HEAR_ABOUT_US):
        if web.elements(Xpath.Input.label_complete(text)):
            web.click(Xpath.Input.label_complete(text))
        else:
            web.click(Xpath.Input.label(text))

    # 13.2. If you were referred by someone, please write their name here.
    refer = data.get_value(TypeformIds.REFER)
    if refer:
        web.input_value(refer, Xpath.Input.referred_by_someone)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # 14.  If you have a promo code, please input it here.
    promo = data.get_value(TypeformIds.PROMO_CODE)
    web.input_value(promo, Xpath.Input.promo_code)
    web.click("//span[@class='page-number']")
    sleep(5)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # 15. I agree to Sol Health's Terms of Service, Privacy Policy, and Telehealth Consent forms.
    web.click(Xpath.Input.tc)

    # ===============================
    web.click(Xpath.Button.next_page)
    # ===============================
    sleep(1)

    # 16. Submit form
    web.click(Xpath.Button.submit_form)

    sleep(5)

    web.wait_for_element(Xpath.Button.sign_out)

    web.quit()


def create_new_form(payload: dict) -> bool:
    if not payload:
        return False

    data = TypeformData(payload)
    first_name = data.get_value(TypeformIds.FIRST_NAME)
    last_name = data.get_value(TypeformIds.LAST_NAME)
    print("START", f"{first_name} {last_name}", datetime.datetime.now())

    try:
        __bot(data, first_name, last_name)
        print("END", f"{first_name} {last_name}", datetime.datetime.now())
        return True
    except Exception as error:
        print("ERROR", str(error))
        return False
