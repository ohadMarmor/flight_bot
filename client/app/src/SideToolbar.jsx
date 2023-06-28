import { useEffect, useState } from 'react';
import axios from 'axios';
import './SideToolbar.css'

function SideToolbar({ name, conversations, onCreateNewConversation, changeChat }) {
  const [conversationMessages, setConversationMessages] = useState([]);

  useEffect(() => {
    // this is to get all the messages of conversation
    const fetchConversationMessages = async (conversationId) => {
      try {
        const response = await axios.get(`http://localhost:5000/api/conversations/${conversationId}/messages`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("jwt")}`,
          },
        });
        return response.data;
      } catch (error) {
        console.log("Error fetching conversation messages:", error);
        return [];
      }
    };

    // here we use the previous function in order to take the first message details to it in the toolbar
    const fetchFirstMessageDate = async () => {
      try {
        const promises = conversations.map((conversation) => fetchConversationMessages(conversation.conversation_id));
        const messages = await Promise.all(promises);
        setConversationMessages(messages);
      } catch (error) {
        console.log("Error fetching conversation messages:", error);
      }
    };

    fetchFirstMessageDate();
  }, [conversations]);

  // Render conversations and their first messages
  return (
    <div className="side-toolbar">
      <div className="conversation-container">
        <h2>Hello {name}!</h2>
        <h3>Conversations</h3>
        <ul className="conversation-list">
          {conversations.map((conversation, index) => {
            const messages = conversationMessages[index];
            const firstMessage = messages ? messages[0] : null;
            const time = firstMessage ? firstMessage.time : 'new conversation';

            return (
              <li key={index}>
                <button onClick={() => changeChat(conversation.conversation_id)}>{`${time}`}</button>
              </li>
            );
          })}
        </ul>
      </div>
      <button className="new-conversation-button" onClick={onCreateNewConversation}>
        Create New Conversation
      </button>
    </div>
  );
}

export default SideToolbar;
