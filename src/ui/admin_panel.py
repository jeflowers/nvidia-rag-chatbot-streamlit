"""Admin panel user interface."""

import streamlit as st

from src.utils.logger import log_activity, get_activity_logs
from src.auth.auth_manager import get_auth_manager


def admin_ui() -> None:
    """Render the admin panel interface."""
    st.title("Admin Panel")
    
    # Return to main app button
    if st.button("Return to Chat"):
        st.session_state.admin_view = False
        st.experimental_rerun()
    
    tab1, tab2, tab3 = st.tabs(["User Management", "Activity Logs", "System Settings"])
    
    with tab1:
        user_management_tab()
    
    with tab2:
        activity_logs_tab()
    
    with tab3:
        system_settings_tab()


def user_management_tab() -> None:
    """Render the user management tab."""
    st.subheader("Create New User")
    
    auth_manager = get_auth_manager()
    
    with st.form("create_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        is_admin = st.checkbox("Admin privileges")
        create_user_submit = st.form_submit_button("Create User")
        
        if create_user_submit:
            if new_username and new_password:
                if auth_manager.user_manager.create_user(new_username, new_password, is_admin):
                    st.success(f"User '{new_username}' created successfully.")
                    log_activity(
                        st.session_state.current_user,
                        "create_user",
                        f"Created user: {new_username}"
                    )
                else:
                    st.error(f"User '{new_username}' already exists.")
            else:
                st.error("Username and password are required.")
    
    st.subheader("Current Users")
    
    users = auth_manager.user_manager.get_all_users()
    
    for username, user in users.items():
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{username}**" + (" (Admin)" if user.is_admin else ""))
        with col2:
            last_login = user.last_login
            if last_login:
                if isinstance(last_login, str):
                    try:
                        from datetime import datetime
                        last_login = datetime.fromisoformat(last_login).strftime("%Y-%m-%d %H:%M")
                    except:
                        pass  # Keep as is if parsing fails
                else:
                    last_login = last_login.strftime("%Y-%m-%d %H:%M")
            else:
                last_login = "Never"
                
            st.write(f"Last login: {last_login}")
        with col3:
            if username != st.session_state.current_user:  # Prevent deleting yourself
                if st.button("Delete", key=f"del_{username}"):
                    auth_manager.user_manager.delete_user(username)
                    log_activity(
                        st.session_state.current_user,
                        "delete_user",
                        f"Deleted user: {username}"
                    )
                    st.experimental_rerun()


def activity_logs_tab() -> None:
    """Render the activity logs tab."""
    st.subheader("User Activity Logs")
    
    logs = get_activity_logs(100)  # Get last 100 logs
    
    if logs:
        for log in logs:
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp = log["timestamp"]
            
            st.write(f"**{timestamp}** - {log['username']} - {log['activity']}" + 
                     (f" - {log['details']}" if log.get('details') else ""))
    else:
        st.info("No activity logs found.")


def system_settings_tab() -> None:
    """Render the system settings tab."""
    st.subheader("System Settings")
    
    auth_manager = get_auth_manager()
    
    # Cleanup expired sessions
    if st.button("Clean Up Expired Sessions"):
        count = auth_manager.session_manager.cleanup_expired_sessions()
        log_activity(
            st.session_state.current_user,
            "cleanup",
            f"Removed {count} expired sessions"
        )
        st.success(f"Removed {count} expired sessions.")
