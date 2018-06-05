from django import forms


def get_radio_input(label, choices=None, initial=None):
    default_choices = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Unknown', 'Unknown'),
    )

    default_initial = 'Unknown'

    if not choices:
        choices = default_choices
        initial = default_initial

    return forms.ChoiceField(
        label=label,
        widget=forms.RadioSelect,
        choices=choices,
        initial=initial,
    )


def get_text_input(label):
    return forms.CharField(
        label=label,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
            }
        ),
        required=False,
    )


def get_number_input(label):
    return forms.CharField(
        label=label,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
            }
        ),
        required=False,
    )


def get_select_input(label, choices=None, initial=None):
    default_choices = (
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Unknown', 'Unknown'),
    )

    default_initial = 'Unknown'

    if not choices:
        choices = default_choices
        initial = default_initial

    return forms.ChoiceField(
        label=label,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        ),
        choices=choices,
        initial=initial,

    )


RADIO = 'radio'
SELECT = 'select'
TEXT = 'text'
NUMBER = 'number'


class Question(forms.Form):
    question_types = [
        RADIO,
        SELECT,
        TEXT,
        NUMBER,
    ]

    question_type = question_types[0]

    def __init__(self, name, label, choices=None, initial=None, question_type='', *args, **kwargs):
        super(Question, self).__init__(*args, **kwargs)

        self.question_type = question_type if self.question_types.__contains__(question_type) else self.question_type

        # adding custom fields
        if self.question_type == RADIO:
            self.fields[name] = get_radio_input(
                label=label,
                choices=choices,
                initial=initial
            )
        elif self.question_type == SELECT:
            self.fields[name] = get_select_input(
                label=label,
                choices=choices,
                initial=initial,
            )
        elif self.question_type == TEXT:
            self.fields[name] = get_text_input(
                label=label,
            )
        elif self.question_type == NUMBER:
            self.fields[name] = get_number_input(
                label=label,
            )
