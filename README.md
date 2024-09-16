# Final Project
**CS50’s Web Programming with Python and JavaScript**
<details>
  <summary>Requirements (Aug-26-2024):</summary>

    In this project, you are asked to build a web application of your own. The nature of the application is up to you, subject to a few requirements:

    - Your web application must be sufficiently distinct from the other projects in this course (and, in addition, may not be based on the old CS50W Pizza project), and more complex than those.
      - A project that appears to be a social network is a priori deemed by the staff to be indistinct from Project 4, and should not be submitted; it will be rejected.
      - A project that appears to be an e-commerce site is strongly suspected to be indistinct from Project 2, and your README.md file should be very clear as to why it’s not. Failing that, it should not be submitted; it will be rejected.
    - Your web application must utilize Django (including at least one model) on the back-end and JavaScript on the front-end.
    - Your web application must be mobile-responsive.

    The most common cause for failure of the final project is not spending enough effort on this next instruction. Read it completely. Your README.md file should be minimally multiple paragraphs in length, and should provide a comprehensive documentation of what you did and, if applicable, why you did it. Ensure you allocate sufficient time and energy to writing a README.md that you are proud of and that documents your project thoroughly, and that distinguishes this project from others in the course and defends its complexity. Simply saying, effectively, “It’s different from the other projects and it was complex to build.” is not at all sufficient justification of distinctiveness and complexity. This section alone should consist of several paragraphs, before you even begin to talk about the documentation of your project.

    - In a README.md in your project’s main directory, include a writeup describing your project, and specifically your file MUST include all of the following:
      - Under its own header within the README called Distinctiveness and Complexity: Why you believe your project satisfies the distinctiveness and complexity requirements, mentioned above.
      - What’s contained in each file you created.
      - How to run your application.
      - Any other additional information the staff should know about your project.
    - If you’ve added any Python packages that need to be installed in order to run your web application, be sure to add them to a requirements.txt file!
    - Though there is not a hard requirement here, a README.md in the neighborhood of 500 words is likely a solid target, assuming the other requirements are also satisfied.

    Failure to adhere to these requirements WILL result in a failing grade for the project, and you will need to wait and resubmit.

    Beyond these requirements, the design, look, and feel of the website are up to you!
</details>

## Eventlink
EventLink is a booking system, allowing for event scheduling and management. The application provides an interface for users to define their availability and provides a link to create events, which is intended to be shared with others who would like to schedule an appointment with the user.

**Registered users**: Can update profile info, set availability, view upcoming events, manage and track event statuses.

**Other users**: Can create and track the events.

### Key Features:
- **User Registration and Authentication**: Users can register, log in, and manage their profiles. The system ensures secure user authentication and session management.
- **Profile and Availability Management**: Users can update their profiles and set their availability, specifying days and time ranges when they are open to schedule events. This feature allows for effective management of user time slots and prevents event conflicts.
- **Event Creation and Tracking**: A shareable link is genereated for each user, this link is used for non-registered users to schedule events with the respective user, specifying details such as date, time, and description. The application supports event scheduling with conflict detection and management, ensuring that events are planned according to user availability.
- **Event Listing and Tracking**: The application displays a list of upcoming and pending events. Users can view details of each event and track their status and cancel events.
- **Pending Event Management**: Users can review and manage pending events, with options to accept or reject them. The system supports adding reasons for rejections.
- **Event History and Search**: A history of past events, including canceled or rejected events and a solution to search events, to help users keep track of their event history.

### Project video: [https://www.youtube.com/watch?v=lJfvyoqAY_A](https://www.youtube.com/watch?v=lJfvyoqAY_A)

## Distinctiveness and Complexity
**Why you believe your project satisfies the distinctiveness and complexity requirements, mentioned above?**

EventLink meet the distinctiveness and complexity requirements by addressing unique challenges not covered by other projects in this course. Here’s why EventLink stands out:

### Distinctiveness:
- **Event Management**: It provides a specialized solution for creating, managing, and tracking events, which is distinct from other projects in this course.
- **Scheduling System**: The project handles intricate scheduling requirements, including the management of user availability and event conflicts. This focus on scheduling and time management sets it apart from projects that do not address date and time features.

### Complexity:
- **Date and Time Handling**: The application deals with complex date and time calculations and validations, including conflict detection. Users can set their availability in different time ranges and handle events based on these settings, which involves intricate logic for managing time slots.
- **Conflict Detection**: Includes logic to detect and resolve scheduling conflicts. It ensures that events do not overlap with users' available time slots and accounts for existing events when creating new ones.
- **Custom Availability Settings**: Users have the ability to set custom availability schedules, which involves managing time ranges and validating input. The system must accommodate varying user preferences and prevent scheduling outside of these parameters.

## Files content
What’s contained in each file you created.

- `capstone`: Main application directory.
  - `static/eventlink`: Contains all static content.
    - `index.js`: Scripts that run in all templates that extends the layout.html template.
        1. If is profile page, generate the create event link, the link is generated based on the current URL and the user id; I decided to use the current URL so this would work in different environments (e.g.: local and codespaces)
        2. If is profile page, sets up a click listener on the copy link button.
        3. If any modal in the page, add listens for click events on modal backdrop to close the modal if clicked outside the modal content area.
        4. Adds a click event listener to the navbar toggler button. This listener toggles the 'show' class on the navbar, enabling the responsive collapse and expand functionality of the navbar for mobile screens.
    - `styles.css`: CSS for all templates that extends the layout.html template.
  - `templates/eventlink`: Contains all templates.
    - `create_event.html`: Event creation page template, contains CSS and JavaScript as it does not extend layout.html template.
    - `event_detail.html`: Event details page template, contains CSS and JavaScript as it does not extend layout.html template.
    - `history.html`: History page template, where all past, rejected and canceled events are listed; Paginated, show a maximum of 10 events per page.
    - `index.html`: Main page template, shows all the upcoming events; Paginated, show a maximum of 10 events per page.
    - `layout.html`: Base template that other templates can extend.
    - `login.html`: Login page template.
    - `pending.html`: Pending events page template, where all created events will be listed to be accepted or rejected; Paginated, show a maximum of 10 events per page.
    - `profile.html`: Profile page template, where user can edit profile data and availability settings.
    - `register.html`: Register page template.
    - `search.html`: Search page template.
  - `admin.py`: Specify models that the super user can edit and create.
  - `apps.py`: Application settings.
  - `models.py`: Contains the models.
    1. `User`: Extends Django's AbstractUser and include additional fields specific to the application.
        - `description`: A text field where users can provide additional information about themselves. It is optional.
        - `default_location`: A character field that allows users to specify a default location for the events. It is optional.
    2. `AvailabilityConfig`: Stores the availability configuration for each user.
        - `user`: A one-to-one relationship with the User model. Each user has a unique availability configuration.
        - `days_availability`: A JSON field that holds the list of available days. Defaults to an empty list.
        - `initial_time`: A time field indicating when the user is available from. It is optional.
        - `end_time`: A time field indicating when the user is available until. It is optional.
        - `event_duration`: A duration field that specifies the default duration of events for the user.
        - `max_days_ahead`: A positive integer field that limits how far in advance events can be created.
    3. `Event`: Represents an event, storing event's details.
        - `user`: A foreign key relationship with the User model, indicating which user the event was created for.
        - `status`: A character field representing the current status of the event. Status can be `Pending`, `Accepted`, `Rejected` or `Canceled`; Defaults to `Pending`.
        - `date_time`: A datetime field indicating when the event is scheduled to occur.
        - `location`: A character field for the event's location. It is optional, as it will not be defined by the user who created the event, but later by the user who accepts the event.
        - `subject`: A character field that provides a title for the event.
        - `description`: A text field for additional details about the event. It is optional.
        - `name`: A character field that stores the event creator's name
        - `email`: An email field that stores the event creator's email.
        - `reason`: A text field to hold the reason for rejection or cancellation of the event. It is optional for creating events, but to reject or cancel an event the user must provide this field.
  - `urls.py`: Contains all application URLs. The `booking` and `event` URLs are dynamic, they take the `user_id` and `event_id` respectively as parameters and display detailed information about a specific user or event.
  - `views.py`: Contains all application views. Most views are protected by the `@login_required` decorator, ensuring that only authenticated users can access them, but some are not and can be accessed by any unregistered user to perform actions such as scheduling events and track event status. The views include basic validation checks and render the appropriate templates with error messages when validation fails. After successful actions (like login, logout, registration, or event creation), users are redirected to the relevant pages (usually the index page or event detail page).

## How to run
0. Make sure you have python and django installed
1. Clone the repository then go to the project directory `cd capstone`
2. Make and apply migrations by running `python manage.py makemigrations` and `python manage.py migrate`.
3. Create a superuser with `python manage.py createsuperuser` *(Optional)*.
4. Run the project with `python manage.py runserver`
4. Go to localhost address and register an account.
