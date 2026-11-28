Development trace:

1 Understanding code structure
simulation.py has the code algorithm implementation
The rest is more like UI and login stuff

2 Reading through simulation.py to pick three pieces of logic to test.

























Summary:
1 Put separating code logic with UI in a skill.
2 make logic as pure as possible 

1. I think refactoring is a very important step. JavaScript requires explicit module setup, while Python makes this simpler. The main idea is to move the core logic into a separate file and organize the calls between files. This lets us test the logic directly from a clean module containing only logic, while keeping the existing application working through those calls.
2. After that, writing test cases is straightforward.
3. I think CI is relatively straightforward too. It essentially means configuring GitHub to run a test file so that every push is checked.
4. Ideally, the core logic and the UI should be kept separate from the beginning.
