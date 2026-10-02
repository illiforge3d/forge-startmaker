import html
import logging
from typing import Optional
from urllib.parse import quote

from pydantic import EmailStr
from src.db.organizations import OrganizationRead
from src.db.users import UserRead
from src.services.email.translations import t
from src.services.email.utils import send_email

logger = logging.getLogger(__name__)


def _send_notification_email(**kwargs):
    """Send mail whose failure must not fail the caller's request.

    Welcome/lifecycle notifications are a side effect of an action that has
    already happened and been committed — the account exists, the org was
    created, the role changed. When the provider is rate-limited or times out,
    raising here turned "no welcome email" into "signup returned 503", which the
    user then retried. Delivery failures are logged and swallowed instead.

    Mail the user is actively waiting on (password reset, invitation, address
    verification) still calls ``send_email`` directly and still raises.
    """
    try:
        return send_email(**kwargs)
    except Exception as e:
        logger.warning("Non-critical email to %s not sent: %s", kwargs.get("to"), e)
        return False


# Public academy — footer "learn more" target, and last-resort CTA fallback.
ACADEMY_URL = "https://university.learnhouse.io"


# Inline SVG logo (StartMaker icon mark + wordmark, scaled down)
LOGO_SVG = """<svg width="127" height="20" viewBox="0 0 1381 218" fill="none" xmlns="http://www.w3.org/2000/svg">
<path transform="translate(-8.29 18.17) scale(0.243785 -0.243785)" d="M242 -15Q161 -15 107.5 3.0Q54 21 34 33L59 99Q80 87 126.5 70.0Q173 53 242 53Q321 53 364.0 81.5Q407 110 407 172Q407 220 383.5 247.5Q360 275 321.5 292.5Q283 310 237 328Q181 350 139.5 374.5Q98 399 75.5 434.5Q53 470 53 524Q53 584 80.0 625.0Q107 666 158.0 687.0Q209 708 279 708Q337 708 386.5 693.5Q436 679 463 662L437 597Q408 617 366.5 629.0Q325 641 278 641Q214 641 173.0 615.0Q132 589 132 530Q132 490 152.0 465.0Q172 440 207.0 423.0Q242 406 286 388Q343 366 388.5 341.5Q434 317 461.0 278.5Q488 240 488 175Q488 112 458.0 70.0Q428 28 373.0 6.5Q318 -15 242 -15Z" fill="black"/>
<g fill="black" transform="translate(154.68 0)">
<path transform="translate(0.00 190.77) scale(0.243785 -0.243785)" d="M242 -15Q161 -15 107.5 3.0Q54 21 34 33L59 99Q80 87 126.5 70.0Q173 53 242 53Q321 53 364.0 81.5Q407 110 407 172Q407 220 383.5 247.5Q360 275 321.5 292.5Q283 310 237 328Q181 350 139.5 374.5Q98 399 75.5 434.5Q53 470 53 524Q53 584 80.0 625.0Q107 666 158.0 687.0Q209 708 279 708Q337 708 386.5 693.5Q436 679 463 662L437 597Q408 617 366.5 629.0Q325 641 278 641Q214 641 173.0 615.0Q132 589 132 530Q132 490 152.0 465.0Q172 440 207.0 423.0Q242 406 286 388Q343 366 388.5 341.5Q434 317 461.0 278.5Q488 240 488 175Q488 112 458.0 70.0Q428 28 373.0 6.5Q318 -15 242 -15Z"/>
<path transform="translate(127.74 190.77) scale(0.243785 -0.243785)" d="M253 -11Q187 -11 149.0 12.0Q111 35 95.5 81.0Q80 127 80 196V668L155 681V518H358V455H155V190Q155 135 167.5 106.0Q180 77 203.5 66.5Q227 56 259 56Q297 56 322.5 65.0Q348 74 363 81L379 20Q364 11 329.5 0.0Q295 -11 253 -11Z"/>
<path transform="translate(223.55 190.77) scale(0.243785 -0.243785)" d="M241 -11Q185 -11 141.0 5.0Q97 21 72.0 57.0Q47 93 47 152Q47 209 75.0 244.5Q103 280 152.5 296.0Q202 312 264 312Q292 312 323.0 307.0Q354 302 362 298V328Q362 362 353.5 393.5Q345 425 319.0 445.0Q293 465 240 465Q185 465 156.0 457.0Q127 449 113 444L103 508Q121 516 158.0 523.0Q195 530 245 530Q316 530 357.5 505.0Q399 480 417.5 436.5Q436 393 436 337V12Q415 7 361.0 -2.0Q307 -11 241 -11ZM252 53Q287 53 315.0 55.5Q343 58 362 62V236Q352 241 328.0 246.0Q304 251 266 251Q234 251 201.0 244.0Q168 237 145.5 216.0Q123 195 123 153Q123 97 158.0 75.0Q193 53 252 53Z"/>
<path transform="translate(348.86 190.77) scale(0.243785 -0.243785)" d="M84 0V494Q110 505 155.5 516.5Q201 528 265 528Q286 528 306.5 525.5Q327 523 343.5 519.5Q360 516 368 513L353 449Q344 453 319.0 457.5Q294 462 255 462Q217 462 192.0 456.5Q167 451 159 447V0Z"/>
<path transform="translate(441.25 190.77) scale(0.243785 -0.243785)" d="M253 -11Q187 -11 149.0 12.0Q111 35 95.5 81.0Q80 127 80 196V668L155 681V518H358V455H155V190Q155 135 167.5 106.0Q180 77 203.5 66.5Q227 56 259 56Q297 56 322.5 65.0Q348 74 363 81L379 20Q364 11 329.5 0.0Q295 -11 253 -11Z"/>
<path transform="translate(537.06 190.77) scale(0.243785 -0.243785)" d="M72 0Q76 92 81.0 183.0Q86 274 92.0 361.5Q98 449 105.0 532.5Q112 616 121 693H191Q220 645 252.5 581.5Q285 518 318.0 448.5Q351 379 381.5 312.0Q412 245 436 191Q460 245 490.5 312.0Q521 379 554.0 448.5Q587 518 620.0 581.5Q653 645 681 693H747Q756 616 763.5 532.5Q771 449 776.5 361.5Q782 274 787.5 183.0Q793 92 797 0H719Q715 102 710.5 200.5Q706 299 700.0 391.0Q694 483 686 565Q676 546 654.5 502.5Q633 459 606.0 402.5Q579 346 551.5 287.0Q524 228 501.5 178.0Q479 128 467 99H400Q388 128 365.5 178.0Q343 228 315.5 287.0Q288 346 261.0 402.5Q234 459 212.5 502.5Q191 546 181 565Q173 483 167.0 391.0Q161 299 156.5 200.5Q152 102 148 0Z"/>
<path transform="translate(748.91 190.77) scale(0.243785 -0.243785)" d="M241 -11Q185 -11 141.0 5.0Q97 21 72.0 57.0Q47 93 47 152Q47 209 75.0 244.5Q103 280 152.5 296.0Q202 312 264 312Q292 312 323.0 307.0Q354 302 362 298V328Q362 362 353.5 393.5Q345 425 319.0 445.0Q293 465 240 465Q185 465 156.0 457.0Q127 449 113 444L103 508Q121 516 158.0 523.0Q195 530 245 530Q316 530 357.5 505.0Q399 480 417.5 436.5Q436 393 436 337V12Q415 7 361.0 -2.0Q307 -11 241 -11ZM252 53Q287 53 315.0 55.5Q343 58 362 62V236Q352 241 328.0 246.0Q304 251 266 251Q234 251 201.0 244.0Q168 237 145.5 216.0Q123 195 123 153Q123 97 158.0 75.0Q193 53 252 53Z"/>
<path transform="translate(874.21 190.77) scale(0.243785 -0.243785)" d="M84 0V763L159 776V290Q183 314 213.0 344.0Q243 374 274.0 406.0Q305 438 332.0 467.0Q359 496 378 518H467Q437 486 396.5 444.0Q356 402 314.5 359.5Q273 317 238 283Q270 261 304.5 227.5Q339 194 373.0 155.0Q407 116 436.5 76.0Q466 36 487 0H400Q370 51 328.0 100.5Q286 150 242.0 191.0Q198 232 159 257V0Z"/>
<path transform="translate(997.33 190.77) scale(0.243785 -0.243785)" d="M311 -11Q220 -11 163.5 24.0Q107 59 80.5 120.0Q54 181 54 259Q54 350 87.0 410.0Q120 470 172.5 500.0Q225 530 283 530Q348 530 395.5 502.5Q443 475 469.0 418.5Q495 362 495 275Q495 268 494.5 258.5Q494 249 493 241H132Q136 153 179.5 104.5Q223 56 315 56Q366 56 398.5 65.5Q431 75 445 82L458 19Q444 11 403.5 0.0Q363 -11 311 -11ZM134 302H419Q418 353 402.0 389.5Q386 426 356.5 445.5Q327 465 284 465Q240 465 207.0 442.0Q174 419 155.5 382.0Q137 345 134 302Z"/>
<path transform="translate(1131.90 190.77) scale(0.243785 -0.243785)" d="M84 0V494Q110 505 155.5 516.5Q201 528 265 528Q286 528 306.5 525.5Q327 523 343.5 519.5Q360 516 368 513L353 449Q344 453 319.0 457.5Q294 462 255 462Q217 462 192.0 456.5Q167 451 159 447V0Z"/>
</g>
</svg>"""

# Shared email styles matching the platform's design system
STYLES = {
    "body": "margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
    "wrapper": "padding: 48px 24px;",
    "container": "max-width: 480px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e5e5e5;",
    "header": "padding: 48px 48px 0 48px; text-align: center;",
    "content": "padding: 36px 48px 48px 48px; text-align: center;",
    "h1": "margin: 0 0 12px 0; font-size: 22px; font-weight: 900; color: #000000; letter-spacing: -0.02em; line-height: 1.3;",
    "p": "margin: 0 0 20px 0; font-size: 14px; color: rgba(0,0,0,0.45); font-weight: 500; line-height: 1.7;",
    "button": "display: inline-block; padding: 14px 32px; background-color: #000000; color: #ffffff; text-decoration: none; border-radius: 10px; font-size: 14px; font-weight: 700; line-height: 1;",
    "link_text": "margin: 24px 0 0 0; font-size: 11px; color: rgba(0,0,0,0.2); word-break: break-all; font-weight: 500; line-height: 1.6;",
    "divider": "margin: 28px 0; border: none; border-top: 1px solid #f0f0f0;",
    "footer": "padding: 0 48px 40px 48px; text-align: center;",
    "footer_text": "margin: 0; font-size: 12px; color: rgba(0,0,0,0.2); font-weight: 500; line-height: 1.6;",
    "code": "display: inline-block; padding: 14px 28px; background-color: #fafafa; border: 1px solid #e5e5e5; border-radius: 10px; font-size: 28px; font-weight: 900; letter-spacing: 0.12em; color: #000000; font-family: monospace;",
}


# Media directory of the square logo variant (see ``upload_org_square_logo``).
# The URL path is the one place the shape of an uploaded logo is knowable
# without a database round-trip, so the renderer keys off it.
SQUARE_LOGO_DIR = "/square_logos/"


def _org_logo_img(logo_url: str, alt: str) -> str:
    """<img> for a white-labeled org logo.

    A square logo (uploaded on the branding page, served from
    ``square_logos/``) sits in a 56px rounded box; a wide logo is letterboxed
    into the same footprint as the StartMaker wordmark. Raster logos (PNG/JPG)
    render in every mail client; an SVG logo may be stripped by some (e.g.
    Gmail), in which case the ``alt`` (the org name) shows instead — still
    org-branded, never a broken StartMaker mark.

    The ``height``/``width`` attributes are for desktop Outlook, whose
    Word-based renderer ignores ``max-width``/``max-height`` and would
    otherwise paint the upload at its native pixel size; every other client
    lets the inline style win.
    """
    src = html.escape(logo_url)
    safe_alt = html.escape(alt)
    if SQUARE_LOGO_DIR in logo_url:
        return (
            f'<img src="{src}" alt="{safe_alt}" width="56" height="56" '
            'style="width: 56px; height: 56px; object-fit: cover; border-radius: 12px; '
            'display: inline-block; border: 0;" />'
        )
    return (
        f'<img src="{src}" alt="{safe_alt}" height="40" '
        'style="max-height: 40px; max-width: 180px; height: auto; width: auto; '
        'display: inline-block; border: 0;" />'
    )


def _org_wordmark(org_name: str) -> str:
    """The org's name set as a wordmark, for orgs that have not uploaded a logo.

    An org-scoped email must never open with the StartMaker mark — the
    recipient has a relationship with the academy, not the platform, and a
    foreign logo above "Reset your Acme Academy password" reads as phishing.
    """
    return (
        f'<span style="display: inline-block; font-size: 20px; font-weight: 900; '
        f'color: #000000; letter-spacing: -0.02em; line-height: 1.2;">'
        f"{html.escape(org_name)}</span>"
    )


def _brand_logo_html(logo_url: str | None, org_name: str) -> str:
    """Header mark for an org-branded email: its logo, else its name."""
    if logo_url:
        return _org_logo_img(logo_url, org_name)
    return _org_wordmark(org_name)


def _button_style(brand_color: str | None) -> str:
    """CTA button style, tinted with the org's brand color when it has one.

    ``brand_color`` must already be normalized (``#rrggbb``) — see
    ``services.email.branding.normalize_brand_color``; anything else keeps the
    default black button rather than risk an unbalanced ``style`` attribute.
    """
    from src.services.email.branding import contrasting_text_color, normalize_brand_color

    color = normalize_brand_color(brand_color)
    if not color:
        return STYLES["button"]
    return (
        STYLES["button"]
        .replace("background-color: #000000;", f"background-color: {color};")
        .replace("color: #ffffff;", f"color: {contrasting_text_color(color)};")
    )


def _powered_by_html(lang: str) -> str:
    """The small "Powered by LearnHouse" line under an org-branded footer."""
    from src.services.email.branding import POWERED_BY_URL

    return (
        f'\n            <p style="{STYLES["footer_text"]} margin-top: 12px;">'
        f'<a href="{POWERED_BY_URL}" style="color: rgba(0,0,0,0.35); text-decoration: none;">'
        f'{t(lang, "common.powered_by")}</a></p>'
    )


def _first_sentence(text: str, limit: int = 110) -> str:
    """Opening sentence of a body string, for use as preheader text.

    Handles the full stops of every locale we ship — the CJK ideographic
    period, the Arabic and Devanagari terminators — then falls back to a word
    boundary. Inbox previews are cut around 100 characters anyway.
    """
    if not text:
        return ""

    for terminator in ("。", "۔", "।", ". ", "! ", "? ", "؟ "):
        head, sep, _tail = text.partition(terminator)
        if sep and len(head) <= limit:
            return (head + sep).strip()

    if len(text) <= limit:
        return text.strip()
    return text[:limit].rsplit(" ", 1)[0].strip() + "…"


def _reply_to_address() -> str:
    """Where a reply to a lifecycle email should land, or "" if unconfigured."""
    try:
        from config.config import get_learnhouse_config

        return (get_learnhouse_config().contact_email or "").strip()
    except Exception:  # pragma: no cover - config is always present in practice
        return ""


def _stat_strip(stats: list[tuple[str, int]]) -> str:
    """A row of label/value pairs, e.g. "LESSONS 8   LEARNERS 0".

    Deliberately not prose. Writing "8 lessons" into copy means solving plural
    agreement in twenty languages — Russian has three forms, Arabic six — and
    without an ICU library the result is "1 lessons" in production. A label
    beside a bare figure needs no agreement in any of them, and it reads faster
    than a sentence anyway.
    """
    if not stats:
        return ""

    cells = []
    for label, value in stats:
        cells.append(
            '<td style="padding: 0 14px; text-align: center;">'
            '<div style="font-size: 22px; font-weight: 900; color: #000000; '
            f'line-height: 1.2;">{value}</div>'
            '<div style="font-size: 10px; font-weight: 700; letter-spacing: 0.08em; '
            'text-transform: uppercase; color: rgba(0,0,0,0.35); margin-top: 2px;">'
            f"{html.escape(label)}</div>"
            "</td>"
        )

    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        'align="center" style="margin: 0 auto 24px auto; border-collapse: collapse;">'
        f"<tr>{''.join(cells)}</tr>"
        "</table>"
    )


def _preheader_block(text: str) -> str:
    """The grey line an inbox list shows after the subject.

    Without one, clients scrape the first visible text — which here is the
    heading, so the list entry reads as the subject said twice. Setting it
    explicitly buys a second line of information in the only place a reader
    looks before deciding to open.

    The zero-width padding after the text stops the client continuing into the
    body copy once the preheader runs out.
    """
    if not text:
        return ""
    padding = "&#847;&zwnj;&nbsp;" * 60
    hide = (
        "display:none;max-height:0;overflow:hidden;mso-hide:all;"
        "font-size:1px;line-height:1px;color:#ffffff;opacity:0;"
    )
    return (
        f'<div style="{hide}">{html.escape(text)}</div>'
        f'<div style="{hide}">{padding}</div>'
    )


def _email_layout(
    title: str,
    body_content: str,
    footer_note: str = "",
    logo_html: str = LOGO_SVG,
    unsubscribe_url: str = "",
    unsubscribe_label: str = "Unsubscribe from these emails",
    preheader: str = "",
    powered_by: bool = False,
    lang: str = "en",
) -> str:
    """Wrap content in the standard email layout.

    ``logo_html`` defaults to the LearnHouse mark; white-labeled emails pass the
    org's logo <img> (or its name as a wordmark) instead.

    ``powered_by`` adds the "Powered by LearnHouse" line to the footer. Only
    org-branded mail sets it, and only when the org's watermark is on — a
    platform email already carries the LearnHouse mark up top.

    ``unsubscribe_url`` is set only by bulk lifecycle mail. Transactional email
    (password reset, invitation, verification) leaves it empty and renders
    byte-identically to before — you cannot unsubscribe from a password reset.
    The link is deliberately legible rather than hidden: someone who wants out
    and can't find the exit reports spam instead, which costs the sending domain
    far more than the opt-out does.
    """
    note_html = ""
    if footer_note:
        note_html = f'\n            <p style="{STYLES["footer_text"]}">{footer_note}</p>'

    unsub_html = ""
    if unsubscribe_url:
        unsub_html = (
            f'\n            <p style="{STYLES["footer_text"]} margin-top: 12px;">'
            f'<a href="{html.escape(unsubscribe_url)}" '
            'style="color: rgba(0,0,0,0.35); text-decoration: underline;">'
            f'{html.escape(unsubscribe_label)}</a></p>'
        )

    powered_html = _powered_by_html(lang) if powered_by else ""

    footer_html = ""
    if note_html or unsub_html or powered_html:
        footer_html = f"""
        <div style="{STYLES['footer']}">
            <hr style="{STYLES['divider']}" />{note_html}{unsub_html}{powered_html}
        </div>"""

    # Prefixed with its own newline so that an absent preheader leaves the
    # document byte-identical to before — the twelve transactional emails
    # share this layout and none of their output may shift.
    block = _preheader_block(preheader)
    preheader_html = f"\n    {block}" if block else ""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="{STYLES['body']}">{preheader_html}
    <div style="{STYLES['wrapper']}">
        <div style="{STYLES['container']}">
            <div style="{STYLES['header']}">
                {logo_html}
            </div>
            <div style="{STYLES['content']}">
                {body_content}
            </div>
            {footer_html}
        </div>
    </div>
</body>
</html>"""


def send_account_creation_email(
    user: UserRead,
    email: EmailStr,
    lang: str = "en",
    cta_url: str | None = None,
    org_name: str | None = None,
    logo_url: str | None = None,
    sender_name: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """Welcome email sent once an account exists.

    ``cta_url`` is where "Get Started" lands: the org-scoped URL when the
    account was created inside an org, or the platform org-picker for org-less
    signups. Falls back to the public academy when no URL is supplied.

    When ``org_name`` is set the email is WHITE-LABELED to that organization:
    the subject and body name the org (not LearnHouse), the org's ``logo_url``
    (or its name) replaces the LearnHouse mark, the button takes the org's
    ``brand_color``, and the footer is reduced to a "Powered by LearnHouse"
    line that ``powered_by=False`` removes. Org-less signups keep the
    LearnHouse-branded variant with the Academy footer link.
    """
    safe_username = html.escape(user.username)
    white_label = bool(org_name)
    safe_org = html.escape(org_name) if org_name else ""

    heading = t(lang, "account_creation.heading", username=safe_username)
    cta = t(lang, "account_creation.cta")

    if white_label:
        subject = t(lang, "account_creation.subject_org", org_name=safe_org, username=safe_username)
        body_text = t(lang, "account_creation.body_in_org", org_name=safe_org)
        footer_note = ""
        logo_html = _brand_logo_html(logo_url, org_name)
    else:
        subject = t(lang, "account_creation.subject", username=safe_username)
        body_text = t(lang, "account_creation.body")
        academy_link = (
            f'<a href="{ACADEMY_URL}" '
            'style="color: rgba(0,0,0,0.35); text-decoration: underline;">'
            f'{t(lang, "academy_link_text")}</a>'
        )
        footer_note = t(lang, "account_creation.footer", academy_link=academy_link)
        logo_html = LOGO_SVG

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        <a href="{html.escape(cta_url or ACADEMY_URL)}" style="{_button_style(brand_color if white_label else None)}">
            {cta}
        </a>
    """

    return _send_notification_email(
        to=email,
        subject=subject,
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=footer_note,
            logo_html=logo_html,
            powered_by=white_label and powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_org_created_email(
    email: EmailStr,
    org_name: str,
    dashboard_url: str,
    lang: str = "en",
):
    """Confirmation email when a user creates a new organization."""
    safe_name = html.escape(org_name)
    heading = t(lang, "org_created.heading", org_name=safe_name)
    body_text = t(lang, "org_created.body")
    cta = t(lang, "org_created.cta")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">{body_text}</p>
        <a href="{html.escape(dashboard_url)}" style="{STYLES['button']}">{cta}</a>
    """
    return _send_notification_email(
        to=email,
        subject=t(lang, "org_created.subject", org_name=safe_name),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "org_created.footer"),
        ),
    )


def send_org_deleted_email(
    email: EmailStr,
    org_name: str,
    lang: str = "en",
):
    """Confirmation email sent to org admins after an organization is deleted."""
    safe_name = html.escape(org_name)
    heading = t(lang, "org_deleted.heading", org_name=safe_name)
    body_text = t(lang, "org_deleted.body")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">{body_text}</p>
    """
    return _send_notification_email(
        to=email,
        subject=t(lang, "org_deleted.subject", org_name=safe_name),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "org_deleted.footer"),
        ),
    )


def send_account_deleted_email(
    email: EmailStr,
    username: str = "",
    lang: str = "en",
):
    """Confirmation ('goodbye') email sent after an account is deleted."""
    heading = t(lang, "account_deleted.heading")
    body_text = t(lang, "account_deleted.body")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">{body_text}</p>
    """
    return _send_notification_email(
        to=email,
        subject=t(lang, "account_deleted.subject"),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "account_deleted.footer"),
        ),
    )


def send_password_reset_email(
    generated_reset_code: str,
    user: UserRead,
    organization: OrganizationRead,
    email: EmailStr,
    base_url: str,
    lang: str = "en",
    sender_name: str | None = None,
    logo_url: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """Password reset for an account inside an organization.

    Branded to the org: its logo (or name) in the header, its color on the
    button, its name as the From display name. Platform-level resets go
    through ``send_password_reset_email_platform`` instead.
    """
    safe_username = html.escape(user.username)
    safe_code = html.escape(generated_reset_code)
    safe_email = quote(str(email), safe='')
    safe_code_param = quote(generated_reset_code, safe='')
    reset_url = f"{base_url}/reset?email={safe_email}&amp;resetCode={safe_code_param}"

    heading = t(lang, "password_reset.heading")
    body_text = t(lang, "password_reset.body", username=safe_username)
    cta = t(lang, "password_reset.cta")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        <div style="margin: 28px 0;">
            <span style="{STYLES['code']}">{safe_code}</span>
        </div>
        <a href="{reset_url}" style="{_button_style(brand_color)}">
            {cta}
        </a>
    """

    return send_email(
        to=email,
        subject=t(lang, "password_reset.subject"),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "password_reset.footer_org"),
            logo_html=_brand_logo_html(logo_url, organization.name),
            powered_by=powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_password_reset_email_platform(
    generated_reset_code: str,
    user: UserRead,
    email: EmailStr,
    base_url: str,
    lang: str = "en",
):
    safe_username = html.escape(user.username)
    safe_code = html.escape(generated_reset_code)
    safe_email = quote(str(email), safe='')
    safe_code_param = quote(generated_reset_code, safe='')
    reset_url = f"{base_url}/reset?email={safe_email}&amp;resetCode={safe_code_param}"

    heading = t(lang, "password_reset.heading")
    body_text = t(lang, "password_reset.body", username=safe_username)
    cta = t(lang, "password_reset.cta")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        <div style="margin: 28px 0;">
            <span style="{STYLES['code']}">{safe_code}</span>
        </div>
        <a href="{reset_url}" style="{STYLES['button']}">
            {cta}
        </a>
    """

    return send_email(
        to=email,
        subject=t(lang, "password_reset.subject"),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "password_reset.footer_platform"),
        ),
    )


def send_invitation_email(
    email: EmailStr,
    org_name: str,
    inviter_username: str,
    signup_url: str,
    invite_code: Optional[str] = None,
    lang: str = "en",
    sender_name: str | None = None,
    logo_url: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """Invitation into an organization, branded to that organization."""
    safe_org_name = html.escape(org_name)
    safe_inviter = html.escape(inviter_username)

    code_section = ""
    if invite_code:
        safe_code = html.escape(invite_code)
        code_hint = t(lang, "invitation.code_hint")
        code_section = f"""
        <div style="margin: 28px 0;">
            <span style="{STYLES['code']}">{safe_code}</span>
        </div>
        <p style="{STYLES['p']}">
            {code_hint}
        </p>"""
    else:
        code_section = f"""
        <p style="{STYLES['p']}">
            {t(lang, "invitation.no_code_hint")}
        </p>"""

    heading = t(lang, "invitation.heading")
    intro = t(lang, "invitation.intro", inviter=safe_inviter, org_name=safe_org_name)
    cta = t(lang, "invitation.cta", org_name=safe_org_name)

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {intro}
        </p>
        {code_section}
        <a href="{signup_url}" style="{_button_style(brand_color)}">
            {cta}
        </a>
    """

    return send_email(
        to=email,
        subject=t(lang, "invitation.subject", org_name=safe_org_name),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "invitation.footer", inviter=safe_inviter),
            logo_html=_brand_logo_html(logo_url, org_name),
            powered_by=powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_org_join_email(
    email: EmailStr,
    username: str,
    org_name: str,
    cta_url: str,
    lang: str = "en",
    logo_url: str | None = None,
    sender_name: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """Greeting sent when an EXISTING account becomes a member of an organization.

    Complements ``send_account_creation_email``, which only fires for brand new
    accounts: a user who already had an account and then joined a second org
    (invite code, open join, OAuth invite, admin provisioning) previously got no
    mail at all and had to find their way to the org on their own.

    Always white-labeled to the org — the user is being welcomed into that
    academy, not onto LearnHouse — with the org's logo (or name) up top.
    """
    safe_username = html.escape(username)
    safe_org_name = html.escape(org_name)

    heading = t(lang, "org_join.heading", username=safe_username)
    body_text = t(lang, "org_join.body", org_name=safe_org_name)
    cta = t(lang, "org_join.cta")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        <a href="{html.escape(cta_url)}" style="{_button_style(brand_color)}">
            {cta}
        </a>
        <p style="{STYLES['link_text']}">{html.escape(cta_url)}</p>
    """

    return _send_notification_email(
        to=email,
        subject=t(lang, "org_join.subject", org_name=safe_org_name),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "org_join.footer", org_name=safe_org_name),
            logo_html=_brand_logo_html(logo_url, org_name),
            powered_by=powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_role_changed_email(
    email: EmailStr,
    username: str,
    org_name: str,
    new_role_name: str,
    lang: str = "en",
    cta_url: str | None = None,
    sender_name: str | None = None,
    logo_url: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """
    Send an email notifying a user that their role has changed in an organization.

    ``cta_url`` is the org's own landing page, on the org's host (verified
    custom domain when it has one). Without it the mail told someone their
    permissions had changed and then gave them nowhere to go.
    """
    safe_username = html.escape(username)
    safe_org_name = html.escape(org_name)
    safe_role_name = html.escape(new_role_name)

    heading = t(lang, "role_changed.heading")
    body_1 = t(
        lang, "role_changed.body_1",
        username=safe_username, org_name=safe_org_name, role=safe_role_name,
    )
    body_2 = t(lang, "role_changed.body_2")

    cta_html = ""
    if cta_url:
        cta_html = (
            f'<a href="{html.escape(cta_url)}" style="{_button_style(brand_color)}">'
            f'{t(lang, "role_changed.cta", org_name=safe_org_name)}</a>'
        )

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_1}
        </p>
        <p style="{STYLES['p']}">
            {body_2}
        </p>
        {cta_html}
    """

    return _send_notification_email(
        to=email,
        subject=t(lang, "role_changed.subject", org_name=safe_org_name),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "role_changed.footer", org_name=safe_org_name),
            logo_html=_brand_logo_html(logo_url, org_name),
            powered_by=powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_email_verification_email(
    token: str,
    user: UserRead,
    organization: OrganizationRead | None,
    email: EmailStr,
    base_url: str,
    lang: str = "en",
    sender_name: str | None = None,
    logo_url: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
):
    """
    Send email verification email with verification link.

    With an ``organization`` the mail is branded to it (its name in the copy,
    its logo or name in the header, its color on the button). Without one it
    is a platform email under the LearnHouse mark.

    Args:
        token: Verification token
        user: User receiving the email
        organization: Organization context (can be None for no-org signups)
        email: Email address to send to
        base_url: Base URL for constructing the verification link
        lang: ISO 639-1 language code for email content (defaults to 'en')

    Returns:
        Boolean indicating if email was sent successfully
    """
    safe_username = html.escape(user.username)
    brand = html.escape(organization.name) if organization else "LearnHouse"
    safe_token = quote(token, safe='')
    safe_user_uuid = quote(user.user_uuid, safe='')
    org_uuid = organization.org_uuid if organization else "none"
    safe_org_uuid = quote(org_uuid, safe='')
    verification_url = f"{base_url}/verify-email?token={safe_token}&amp;user={safe_user_uuid}&amp;org={safe_org_uuid}"

    heading = t(lang, "email_verification.heading")
    body_text = t(lang, "email_verification.body", username=safe_username, brand=brand)
    cta = t(lang, "email_verification.cta")
    copy_paste = t(lang, "email_verification.copy_paste")

    body_content = f"""
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        <a href="{verification_url}" style="{_button_style(brand_color if organization else None)}">
            {cta}
        </a>
        <p style="{STYLES['link_text']}">
            {copy_paste}<br />{verification_url}
        </p>
    """

    return send_email(
        to=email,
        subject=t(lang, "email_verification.subject"),
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "email_verification.footer", brand=brand),
            logo_html=_brand_logo_html(logo_url, organization.name) if organization else LOGO_SVG,
            powered_by=bool(organization) and powered_by,
            lang=lang,
        ),
        sender_name=sender_name,
    )


def send_nudge_email(
    nudge_id: str,
    email: EmailStr,
    org_name: str,
    cta_url: str,
    unsubscribe_url: str,
    lang: str = "en",
    logo_url: str | None = None,
    has_cta: bool = True,
    track: str = "",
    stats: list[tuple[str, int]] | None = None,
    sender_name: str | None = None,
    brand_color: str | None = None,
    powered_by: bool = True,
    **copy_vars,
):
    """Send one lifecycle nudge.

    Generic over the catalog: the nudge id selects its copy from the
    ``nudge.<id>.*`` namespace, so adding a nudge never means adding a function
    here. ``copy_vars`` fills the placeholders that nudge's strings declare
    (course name, plan name, and so on) — every value is escaped before it
    reaches the template.

    ``track`` selects the illustration. It is drawn as a table mosaic rather
    than an image because Gmail strips inline SVG and both Gmail and Outlook
    block ``data:`` URIs, so an embedded picture would render as a blank gap
    for a large share of readers.

    Unlike transactional mail this always carries an unsubscribe link and the
    matching ``List-Unsubscribe`` headers. Gmail and Outlook expect them on
    bulk mail, and without them a run at any real volume puts the sending
    domain at risk.

    Failures are swallowed via ``_send_notification_email``: a nudge nobody
    asked for must never be the reason a batch job dies.
    """
    safe_org_name = html.escape(org_name)
    raw_vars = {key: str(value) for key, value in copy_vars.items() if value is not None}
    raw_vars.setdefault("org_name", org_name)
    safe_vars = {key: html.escape(value) for key, value in raw_vars.items()}

    heading = t(lang, f"nudge.{nudge_id}.heading", **safe_vars)
    body_text = t(lang, f"nudge.{nudge_id}.body", **safe_vars)
    # The subject is plain text, not HTML: escaping it would deliver
    # "Maths &amp; Physics" to the inbox, and ampersands in course names are
    # common enough that this is not an edge case.
    subject = t(lang, f"nudge.{nudge_id}.subject", **raw_vars)

    from src.services.nudges.illustrations import render_illustration

    stat_html = _stat_strip(
        [(t(lang, f"nudge.stat.{key}"), value) for key, value in (stats or [])]
    )

    body_content = f"""
        {render_illustration(track)}
        <h1 style="{STYLES['h1']}">{heading}</h1>
        <p style="{STYLES['p']}">
            {body_text}
        </p>
        {stat_html}"""
    if has_cta and cta_url:
        cta = t(lang, f"nudge.{nudge_id}.cta", **safe_vars)
        body_content += f"""
        <a href="{html.escape(cta_url)}" style="{_button_style(brand_color)}">
            {cta}
        </a>
        <p style="{STYLES['link_text']}">{html.escape(cta_url)}</p>
    """

    # The preheader is the body's opening sentence rather than a thirty-first
    # set of translated strings. It is already localised, and it gives the
    # inbox list a second line of information instead of echoing the subject.
    preheader = _first_sentence(t(lang, f"nudge.{nudge_id}.body", **raw_vars))

    headers: dict[str, str] = {}
    if unsubscribe_url:
        headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    # Several nudges invite a reply. Without this they would arrive from the
    # no-reply sender and the invitation would be a lie.
    reply_to = _reply_to_address()
    if reply_to:
        headers["Reply-To"] = reply_to

    return _send_notification_email(
        to=email,
        subject=subject,
        body=_email_layout(
            title=heading,
            body_content=body_content,
            footer_note=t(lang, "nudge.common.footer", org_name=safe_org_name),
            logo_html=_brand_logo_html(logo_url, org_name),
            unsubscribe_url=unsubscribe_url,
            unsubscribe_label=t(lang, "nudge.common.unsubscribe"),
            preheader=preheader,
            powered_by=powered_by,
            lang=lang,
        ),
        headers=headers or None,
        sender_name=sender_name,
    )
