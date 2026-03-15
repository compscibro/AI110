# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

What did the game look like the first time you ran it?
  - [x] After running the game for the first time, the UI looked simple and on point, but there were issues with some of the functionalities.

List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  - [x] Some of the concrete bugs that I noticed at the start were:
    - In difficulty level - Normal:
    1. After running the game for the first time, even without submitting any guesses, game have already counted 1 attempt, which should have been 0 attempts.
    2. On the left hand side of the screen, it shows that 8 attempts are allowed but in the center of the screen
    it shows that only 7 attempts left.
    3. After submitting the first guess, 67, the game did not update the number of attempts left. The left hand side of the screen still showed 8 attempts allowed, while the center of the screen showed 7 attempts left.
      3.1. After submitting the first guess, 67, the hint was displayed but the hint was incorrect. The secret
      number was 81, I entered 67, but the hint said "Go lower."
    4. After entering a new number, 69, but before submitting the guess, then the attempts left changed to 6 in the center of the screen, but the left hand side of the screen still showed 8 attempts allowed.
    5. The "New Game" button did reset the attempts left to 8, but initially it was 7 after running the game for the first time, even before submitting any guesses.
      5.1 The "New Game" button did not clear the history of my guesses. After clicking the "New Game" button, the history of my previous guesses (67 and 69) was still displayed on the screen.
      5.2 The "New Game" button did not reset the score to 0 either, it kept the score from the previous game.
    6. The history is not properly keeping track of the guesses being submitted.
    7. After submitting the correct guess, 90, it shows that it's correct, but it also shows that the final
    score is 70, however, in developer debug info, it shows that the score is 0.
---

## 2. How did you use AI as a teammate?

Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- [x] I used Claude Code in Ask, AutoEdit, and Plan mode through VS Code chat feature. I also created a .claude folder containing the rules folder, which has 4 .md files:
  1. change_log.md: this file contains the changes that have been made upon my approval of the AI suggestions.
  2. code.md: this file contains guidelines regarding the code structure, requirements, modularity, readability,
  style, and best practices.
  3. comments.md: this file contains guidelines regarding the comments in the code, such as when to comment, what to comment, and how to comment.
  4. test.md: this file contains guidelines regarding testing, such as when to test, what to test, and how to test.

Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- [x] AI suggested that that if "attempts" is not in st.session_state, then the st.session_state.attempts should be initialized to 0. I verified by reviewing the code, which made
sense and I approved the change. After making the change, I ran the game again and saw that the initial attempts left were set
to 8 instead of 7.
Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
- [x]
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
