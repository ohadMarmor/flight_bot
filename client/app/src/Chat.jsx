import React, { useState, useEffect } from 'react';
import './Chat.css';
import '@chatscope/chat-ui-kit-styles/dist/default/styles.min.css';
import { MainContainer, ChatContainer, Message, MessageList, MessageInput, TypingIndicator } from '@chatscope/chat-ui-kit-react';
import SideToolbar from './SideToolbar'
import axios from "axios";
import './background.css';
import './widget.css';
import './RecommenderSystem.css';


// Get the JWT from the query parameter in the URL
const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

const welcomeMessages = [
  {
    content: "Hello! I am your SporTrip flight bot! I am here to help you, the sports fan, to find your next journey!",
    is_user: false,
    time: "just now"
  },
  {
    content: "Please tell me what you are looking for. For example: 'Hi, I want to fly to watch a football game, and I want a place with skiing, spicy food, and shopping.'",
    is_user: false,
    time: "just now"
  },
  {
    content: "I will do my best to help you by finding you tickets and events that would fit your choices.",
    is_user: false,
    time: "just now"
  },
  {
    content: "Here are some instructions to guide you along the way:",
    is_user: false,
    time: "just now"
  },
  {
    content: "1. Discuss your preferences with me, such as sports events, destinations, and activities.",
    is_user: false,
    time: "just now"
  },
  {
    content: "2. When setting the date for the flight, please use the format: 'DATES: YYYY-MM-DD YYYY-MM'. The first date is the departure, and the second is the return. You can also choose to specify only the month.",
    is_user: false,
    time: "just now"
  },
  {
    content: "3. When you're ready to see the results, send a message in this format: 'SUBMIT X', where X is the number of passengers (between 1 and 12).",
    is_user: false,
    time: "just now"
  },
  {
    content: "After the submit message, feel free to keep asking me for other options and specify your preferences to help me find the best option for you!",
    is_user: false,
    time: "just now"
  }
];



function Chat() {
  const [messages, setMessages] = useState(welcomeMessages);
  const [isTyping, setIsTyping] = useState(false);


  const [conversations, setConversations] = useState([]);

  const [conversationId, setConversationId] = useState(-1)

  const [name, setName] = useState([])

  const [recommendation, setRecommendation] = useState('Loading our recommendation...⌛');

  const fetchConversations = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/conversations", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`,
        },
      });
      const conversations_db = response.data;
      setConversations(conversations_db);

      // Get the conversation ID of the last conversation
      if (conversations_db.length > 0) {
        const lastConversationId = conversations_db[conversations_db.length - 1].conversation_id;
        changeChat(lastConversationId)
      } else {

      }
    } catch (error) {
      console.log("Error fetching conversations:", error);
    }
  };

  const fetchUserName = async () => {
    try {
      const reaponse = await axios.get("http://localhost:5000/api/users", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`,
        },
      });
      const user_name = reaponse.data.name
      setName(user_name)
    } catch (error) {
      console.log("Error fetching name:", error);
    }
  }

  const fetchRecommendation = async () => {
    try {
      const response = await axios.get("http://localhost:5000/api/recommendation", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`,
        },
      });
      const r = response.data;
      setRecommendation(r.recommendation);
      console.log(recommendation)
    } catch (error) {
      console.log("Error fetching recommendation:", error);
    }
  };
  

  const changeChat = async (conId) => {
    setConversationId(conId);
    setMessages(welcomeMessages);
    // Fetch messages for the last conversation
    const messagesResponse = await axios.get(`http://localhost:5000/api/conversations/${conId}/messages`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("jwt")}`,
      },
    });
    const messages = messagesResponse.data;
    
    // Update the messages state with the fetched messages only if they exist
    if (messages.length > 0) {
      setMessages(messages);
    }
  }


  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://widgets.kiwi.com/scripts/widget-search-iframe.js';
    script.setAttribute('data-currency', 'EUR');
    script.setAttribute('data-lang', 'en');
    script.setAttribute('data-affilid', 'ohadmarmorflights');
    script.setAttribute('data-results-only', 'true');
    script.async = true;
  
    document.getElementById('widget-holder').appendChild(script);
  
    return () => {
      document.getElementById('widget-holder').removeChild(script);
    };
  }, []);


useEffect(() => {
  
  fetchConversations();
  fetchUserName();
  fetchRecommendation();
}, []);


  
const handleCreateNewConversation = async () => {
  try {
    const response = await axios.post("http://localhost:5000/api/conversations", null, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("jwt")}`,
      'Content-Type': 'application/json'
      }
    });

    console.log(response.data);
    const newConversation = response.data;
    setConversationId(newConversation.conversation_id);

    // Fetch messages for the last conversation
    const messagesResponse = await axios.get(
      `http://localhost:5000/api/conversations/${newConversation.conversation_id}/messages`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("jwt")}`
        }
      }
    );
    const messages = messagesResponse.data;
    // Update the messages state with the fetched messages
    if (messages.length > 0)
          {
            setMessages(messages);
          } else {
            setMessages(welcomeMessages)
          }
  } catch (error) {
    console.log("Error creating conversation:", error);
  }
  // Fetch updated conversations list
  fetchConversations();
};


  const handleSend = async (message) => {
    // this condiotion is to prevent the user to send messages during the bot proccessin a response:
    if (!isTyping) {
      const newMessage = {
      content: message,
      is_user: true,
      conversation_id: conversationId
      };
      const newMessages = [...messages, newMessage];
      // we want to view the message the user just sent before receiving the response because it may take a while
      setMessages(newMessages);
      // and now we activate the state that ignoring messages
      setIsTyping(true);
      try {
        const response = await axios.post(
          'http://localhost:5000/api/messages', newMessage,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("jwt")}`,
              'Content-Type': 'application/json'
            }
          }
        );
        // after getting the response, we view it in the chat window
        const newMessagesWithResponse = [...newMessages, response.data];
        setMessages(newMessagesWithResponse);
        // now the user can sending message again
        setIsTyping(false);
      } catch (error) {
        console.log('Error creating message:', error);
      }
    // await processMessageToChatBot(newMessages);
    }
  };

  async function processMessageToChatBot(chatMessages) {
    
  }
/*
  const htmlContent = `
  <div id="widget-holder"></div>
  <script 
  data-currency="EUR" 
  data-lang="en" 
  data-affilid="ohadmarmorflights" 
  data-results-only="true" 
  src="https://widgets.kiwi.com/scripts/widget-search-iframe.js">
  </script>
  `;
*/
return (
  <div>
    <div className="page-container">
      <div className="recommendation-container">
        <div className="recommendation-box">
          <div className="recommendation" dangerouslySetInnerHTML={{ __html: recommendation }}></div>
        </div>
      </div>
      <div className="chat-container">
        <SideToolbar name={name} conversations={conversations} onCreateNewConversation={handleCreateNewConversation} changeChat={changeChat} />
        <div className="chat-screen">
          <div style={{ position: "relative", height: "550px", width: "500px" }}>
            <MainContainer>
              <ChatContainer>
              <MessageList 
                  scrollBehavior="smooth" 
                  typingIndicator={isTyping ? <TypingIndicator content="bot is typing..." /> : null}
                >
                  {messages.map((message, i) => {
                    return <Message key={i} model={{
                      message: message.content,
                      sentTime: new Date(message.time),
                      direction: message.is_user ? 'outgoing' : 'incoming',
                    }} />;
                  })}
                </MessageList>
                <MessageInput placeholder="Type message here" onSend={handleSend} />
              </ChatContainer>
            </MainContainer>
          </div>
        </div>
        <div className="widget-frame">
          <div id="widget-holder"></div>
        </div>
      </div>
    </div>
  </div>
);

  
  
}

export default Chat;
