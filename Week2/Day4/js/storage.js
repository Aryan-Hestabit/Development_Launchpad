const KEY = "todos";

export function loadTodos() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || [];
  } catch (err) {
    throw new Error("Failed to load todos");
  }
}

export function saveTodos(todos) {
  try {
    localStorage.setItem(KEY, JSON.stringify(todos));
  } catch (err) {
    throw new Error("Failed to save todos");
  }
}
