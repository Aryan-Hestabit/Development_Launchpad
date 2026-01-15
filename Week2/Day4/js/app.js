import { loadTodos, saveTodos } from "./storage.js";
import { debounce } from "./utils.js";

const form = document.getElementById("todoForm");
const input = document.getElementById("todoInput");
const list = document.getElementById("todoList");

let todos = [];

function render() {
  list.innerHTML = "";
  todos.forEach((todo, index) => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="todotext">${todo}</span>
      <div>
        <button class="listbutton" onclick="editTodo(${index})">✏️</button>
        <button class="listbutton" onclick="deleteTodo(${index})">❌</button>
      </div>
    `;
    list.appendChild(li);
  });
}

function normalize(text){
    return text.toLowerCase().replace(/\s+/g, "");
}

function init() {
  try {
    todos = loadTodos();
    render();
  } catch (err) {
    logError(err);
  }
}

form.addEventListener("submit", e => {
  e.preventDefault();
  const newTodo = input.value.trim();
  if(!newTodo) return;

  const exist = todos.some(
    todo => normalize(todo) === normalize(newTodo)
  );

  if (exist) {
    alert("Task already in the Todo list");
    return;
  }

  todos.push(newTodo);
  saveTodos(todos);
  input.value = "";
  render();
});

window.deleteTodo = index => {
  todos.splice(index, 1);
  saveTodos(todos);
  render();
};

window.editTodo = index => {
  const updated = prompt("Edit todo:", todos[index]);
  if (updated !== null) {
    todos[index] = updated;
    saveTodos(todos);
    render();
  }
};

const logError = debounce(err => {
  console.error(err);
}, 500);

init();
