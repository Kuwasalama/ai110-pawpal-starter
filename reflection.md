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

My scheduler looks at a few things when it builds the day. The main one is time,
which is how many minutes the owner says they have. That's the hard limit,
because no matter what, you can't fit more than the day actually has room for.
The second one is priority, where every task is low, medium, or high, and higher
priority tasks get planned first. Duration matters too, both as a tie-breaker
(if two tasks are the same priority, the longer one goes first) and because it
decides whether a task even fits or has to be shortened. Then there's the owner's
own preferences, like the time they want to start the day, and the option to pin
a task to a set time or mark it as important so it jumps ahead. Finally it checks
for conflicts, meaning two tasks pinned to times that overlap, and warns the owner
about it.

For deciding what mattered most, I thought about it like a real morning. Time is
at the very top because it's a limit I can't argue with, it just is what it is.
After that comes what the owner directly tells me, so if they pinned a task to a
specific time or marked it important, that beats everything else, because the
person actually living the day knows things my code doesn't (like a vet
appointment that can't move). If the owner didn't say anything special, then I
fall back on priority, and duration is just the tie-breaker under that. So the
order in my head was: time is the boundary, the owner's own choices win inside
that boundary, and priority handles everything they didn't specifically call out.

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

I used AI a lot on this project, mostly for the more technical stuff. There were
parts I didn't really know how to do, like the sorting logic and the date math
for repeating tasks, so I leaned on it to help me get those working.

I also used it to understand things I didn't get. When something confused me I
would just ask it to explain, and it would break it down in a way that made sense
instead of me being stuck. So it wasn't only writing code for me, it was kind of
teaching me while we went.

The other big thing was debugging. When something broke or didn't do what I
wanted, I'd ask it what was going on and it helped me figure out the problem. And
I used it to make my code easier to read too, like cleaning things up and adding
comments so it isn't a mess when someone else looks at it.

**b. Judgment and verification**

There were times I said no to what the AI suggested. One that stands out is when
it told me I should pick the shorter tasks first so I could fit more of them into
the day. It wasn't a bad idea, but I said no, because I liked the way I already
had it and I wanted the app to stay simple and easy for a user to follow. Another
time it pushed some more technical changes, and I turned those down too, because I
wanted to keep it at a level I could actually understand instead of adding stuff
just because it sounded smart.

Some of its suggestions were honestly good, I'm not going to act like they
weren't. But a lot of the time I still went with my own anyway. I'd rather use my
own idea and have it not work perfectly, and know that it was me who made that
call, than take the AI's idea and have it work but not really feel like mine.
Understanding my own project mattered more to me than making it the "smartest"
version possible.

For actually checking things, I didn't just trust that the code looked right. I
ran main.py and read the output myself, and I ran my tests to see if stuff passed.
That's how we caught a real bug where the program crashed on Windows because of a
special character, which I never would have seen just by reading it.

---

## 4. Testing and Verification

**a. What you tested**

I tested the parts of the scheduler that actually make decisions, since those are
the ones that would hurt the most if they broke. First I have the basic ones,
that marking a task complete flips it from not done to done, and that adding a
task to a pet actually grows that pet's list. Then I have the three that cover the
real logic. One checks that sorting returns the pinned tasks in the right time
order, so I added them out of order on purpose and made sure they came back
earliest first. Another checks recurrence, that completing a daily task creates a
brand new task for the next day and attaches it to the pet. And the last one
checks conflict detection, that when two tasks are booked for the same time the
scheduler actually flags it and names both tasks.

These tests mattered because they're the features that are easy to get subtly
wrong and hard to notice by eye. Sorting, repeating tasks, and conflicts all have
little edge cases hiding in them, so having a test means if I change something
later and accidentally break one, it'll tell me instead of me shipping it broken.

**b. Confidence**

Confidence level: five stars. All five of my tests pass, and they cover the most
important behaviors (sorting, recurring tasks, and conflict detection), so I feel
really good about how the core of it works. I'm not going to say it's perfect,
because I know my test coverage isn't huge, but for the main stuff the scheduler
is supposed to do, I trust it.

If I had more time, the edge cases I'd test next are the ones sitting right on the
boundaries, since that's where bugs like to hide. I'd test a pet with no tasks and
an owner with no pets at all, just to make sure it doesn't crash on an empty
schedule. I'd test two tasks that touch but don't actually overlap (like one
ending at 10:30 and the next starting at 10:30) to make sure it does NOT wrongly
call that a conflict. I'd test the shortening cutoff, so a task with exactly half
its time free versus just under half, to make sure it shortens in one case and
gets left off in the other. And I'd test a one-off task to confirm completing it
does not create a next copy, plus an unknown priority label to make sure a typo
doesn't crash the sort.

---

## 5. Reflection

**a. What went well**

The part I'm most satisfied with is the scheduling logic, because that's the part
that actually made me think. It wasn't just typing out code, I had to sit there
and make real decisions, like should the scheduler do the long tasks first or not,
and what happens when everything doesn't fit. For a lot of it I put myself in the
customer's shoes and thought about how I'd react if the app did a certain thing,
like if it just silently dropped my pet's walk I'd be annoyed, so that pushed me
toward shortening the task instead of skipping it.

There were a lot of pros and cons to weigh on almost every choice, and some of it
was me going back and forth on ideas the AI suggested too, deciding what I
actually wanted versus what sounded good. That whole part really required me to
think it through instead of just following steps, and that's exactly why I'm the
most proud of it.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

The biggest thing I learned was what it actually feels like to be the lead
architect while using AI tools. You don't just follow the AI blindly. And I'm not
saying that to discredit it, because it genuinely did a lot of work for me and
saved me time. But sometimes it makes mistakes, kind of like we do, or it
hallucinates and gives you something that isn't really right. So you can't just
accept everything. On top of that, you have to guide it to get what you actually
want, because it'll throw suggestions at you and sometimes you just don't like
them or they don't fit your design. At the end of the day I'm the one who has to
know what I'm building and make the final call. The AI is a really strong helper,
but the direction and the decisions are still on me, and that's what made it feel
like I was the architect and not just someone copying answers.
