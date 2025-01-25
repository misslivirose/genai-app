// Get checklist elements
const checklistInput = document.getElementById('checklist-input');
const addTaskButton = document.getElementById('add-task-button');
const checklist = document.getElementById('checklist');

// Function to add a new task
function addTask() {
    const taskText = checklistInput.value.trim();
    if (taskText === '') return;

    // Create a new task item
    const taskItem = document.createElement('li');
    const taskTextSpan = document.createElement('span');
    taskTextSpan.textContent = taskText;
    taskTextSpan.className = 'task-text';

    // Task actions (complete & delete)
    const completeButton = document.createElement('button');
    completeButton.textContent = 'Complete';
    completeButton.addEventListener('click', () => {
        taskItem.classList.toggle('completed');
    });

    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'Delete';
    deleteButton.addEventListener('click', () => {
        taskItem.remove();
    });

    // Add text and actions to the task item
    const taskActions = document.createElement('div');
    taskActions.className = 'task-actions';
    taskActions.appendChild(completeButton);
    taskActions.appendChild(deleteButton);

    taskItem.appendChild(taskTextSpan);
    taskItem.appendChild(taskActions);

    // Add the task item to the checklist and clear the input
    checklist.appendChild(taskItem);
    checklistInput.value = '';
}