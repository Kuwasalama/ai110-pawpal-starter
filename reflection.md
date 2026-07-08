# PawPal+ Project Reflection

## 1. System Design
Pawpal+ is a smart pet care planner that tracks pet care tasks, considers owners constraints and preferences, and generates personalized daily schedules with clear explanations for it's recommendations.

**a. Initial design**
The design consists of four main classes. Owner, pet, task and scheduler.
Each class has it's own responsibilities. The owner owns the pets and controls the constraints(for scheduling and the like). The Pet has a list of basic tasks it needs and it's information. Task: states the task, priority, duration, then turns into sumn the scheduler can sort by.
last but not least, the Scheduler. Basically the engine; the scheduler reads tasks plus the owners constraints and makes a plan.

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

Yes, my design changed a few times once I started building it.

First, I had the tasks and the scheduler set up separately, so I had to hand
the scheduler its list of tasks myself. That felt off because it could end up
planning from the wrong list. So I changed it so the scheduler just goes and
grabs the tasks straight from each pet. Now it always uses the real lists.

Second, the part that checks if a task fits only knew the total free time for
the whole day, not how much I'd already used up. So it would keep saying yes
and overfill the day. I fixed it so it also knows how much time is actually
left, and it stops once the day is full.

The last change was the one I went back and forth on the most. At first, if a
task didn't fit, I just skipped it. But that bugged me because a pet owner
would not be happy hearing their pet's walk or playtime got dropped. So I
changed it so if there's still a decent chunk of time left (at least half of
what the task needs), the task still happens, just for a shorter time. If
there's really not enough time for even that, it gets left off, but the app
says so clearly instead of hiding it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The first tradeoff is in how my scheduler picks the order to do tasks. It goes
by highest priority first, and if two tasks are the same priority, it does the
longer one first. This is simple and easy to explain to the owner, but it isn't
always the smartest choice. Sometimes doing one long task first means two or
three shorter tasks don't fit anymore, when really those shorter ones might have
mattered more to the owner. I decided to keep the simple version anyway, because
it's predictable and I didn't want the app making confusing choices. Instead of
making the scheduler super complicated, I added a feature where the owner can
mark a task as important or give it a set time, and then it jumps to the front
even if it's short. So the person, who actually knows what matters that day, gets
to make the call the algorithm can't really make on its own.

The second tradeoff is about testing. As I kept adding more logic (sorting by
time, filtering tasks, repeating tasks, and detecting conflicts), I mostly
checked that things worked by running main.py and reading the output with my own
eyes. That was fast and it let me see each new feature actually working, but it
means I only have a couple of real automated tests. The tradeoff is that I don't
have a strong safety net. If I change something later, a test probably won't warn
me that I broke one of these features. Basically, the deeper my logic got, the
weaker my testing got, and if I had more time that's the first thing I'd go back
and fix.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
