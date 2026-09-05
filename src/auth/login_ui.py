import streamlit as st


def require_login() -> bool:
    """Shows a 'Log in with Google' screen if the user isn't authenticated.

    Returns True once Streamlit's native auth confirms a logged-in Google
    user (st.user is populated automatically after st.login() completes
    the OAuth redirect). No passwords or OTP codes are handled by this app
    at all — Google verifies the user's identity.
    """
    if st.user.is_logged_in:
        return True

    left, center, right = st.columns([1, 1.4, 1])

    with center:
        st.markdown(
            """
            <div style="text-align:center; margin-top: 4rem;">
                <div style="font-size:2.4rem;">🏔️</div>
                <h1 style="margin-top:0.2rem;">Pahad-Guard</h1>
                <h3 style="font-weight:600; margin-top:0.3rem;">Login required</h3>
                <p style="color:#93A398; max-width:32rem; margin:0.6rem auto 0;">
                    Sign in with your Google account to access the risk
                    dashboard and manage alert subscriptions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        btn_left, btn_mid, btn_right = st.columns([1, 2, 1])
        with btn_mid:
            st.button(
                "🔐 Log in with Google",
                type="primary",
                on_click=st.login,
                use_container_width=True,
            )

    return False


def render_logout_control() -> None:
    if not st.user.is_logged_in:
        return

    st.sidebar.markdown("---")
    name = st.user.get("name") or st.user.get("email", "user")
    st.sidebar.caption(f"Logged in as: {name}")
    if st.sidebar.button("Log out"):
        st.logout()


def current_user_email() -> str | None:
    if st.user.is_logged_in:
        return st.user.get("email")
    return None
