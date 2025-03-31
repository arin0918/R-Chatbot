import React, { useState } from "react";
import axios from "axios";

const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Function to send message to Rasa
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", message: input };
    setMessages([...messages, { text: input, type: "user" }]);
    setInput("");

    try {
      const response = await axios.post(
        "http://localhost:5005/webhooks/rest/webhook",
        userMessage
      );

      if (response.data.length > 0) {
        const botReply = response.data[0].text;
        setMessages([...messages, { text: input, type: "user" }, { text: botReply, type: "bot" }]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages([...messages, { text: "Error connecting to bot", type: "bot" }]);
    }
  };

  return (
    <div style={styles.container}>
      <h2>Customer Chatbot</h2>
      <div style={styles.chatWindow}>
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              ...styles.message,
              alignSelf: msg.type === "user" ? "flex-end" : "flex-start",
              backgroundColor: msg.type === "user" ? "#4CAF50" : "#0084FF",
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div style={styles.inputContainer}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
        />
        <button style={styles.button} onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

// CSS styles
const styles = {
  container: { width: "400px", margin: "auto", textAlign: "center" },
  chatWindow: { height: "400px", overflowY: "auto", padding: "10px", border: "1px solid #ddd" },
  message: { padding: "10px", borderRadius: "10px", color: "white", margin: "5px", maxWidth: "75%" },
  inputContainer: { display: "flex", marginTop: "10px" },
  input: { flex: 1, padding: "10px", border: "1px solid #ddd" },
  button: { padding: "10px", backgroundColor: "#007BFF", color: "white", border: "none", cursor: "pointer" },
};

export default App;
