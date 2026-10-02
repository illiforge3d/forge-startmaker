import {
  Body,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Preview,
  Section,
  Text,
} from '@react-email/components'
import * as React from 'react'

// Shared transactional email layout (React Email). One flexible template drives
// every message — welcome, purchase, plan change, payment failed, etc. — via an
// accent color plus optional card / transition / bullet blocks. Ported from the
// platform repo's templates/shared.tsx and kept provider-agnostic (rendered to
// HTML by services/emails/resend.ts).

export interface InfoCard {
  label: string
  title: string
  caption?: string
  color: string
}

export interface TransitionCard {
  fromLabel: string
  fromValue: string
  fromColor: string
  toLabel: string
  toValue: string
  toColor: string
}

export interface LearnHouseEmailProps {
  accentColor: string
  heading: string
  subtitle: string
  body?: string
  bulletPoints?: string[]
  card?: InfoCard
  transition?: TransitionCard
  /** Optional call-to-action. */
  cta?: { label: string; href: string }
}

// The StartMaker wordmark inlined as a data URI so transactional emails render
// it without external hosting (some clients strip SVG — the alt shows instead).
// Set EMAIL_LOGO_URL to point at a hosted logo instead.
const LOGO_URL =
  process.env.EMAIL_LOGO_URL ||
  'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTI3IiBoZWlnaHQ9IjIwIiB2aWV3Qm94PSIwIDAgMTM4MSAyMTgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKC04LjI5IDE4LjE3KSBzY2FsZSgwLjI0Mzc4NSAtMC4yNDM3ODUpIiBkPSJNMjQyIC0xNVExNjEgLTE1IDEwNy41IDMuMFE1NCAyMSAzNCAzM0w1OSA5OVE4MCA4NyAxMjYuNSA3MC4wUTE3MyA1MyAyNDIgNTNRMzIxIDUzIDM2NC4wIDgxLjVRNDA3IDExMCA0MDcgMTcyUTQwNyAyMjAgMzgzLjUgMjQ3LjVRMzYwIDI3NSAzMjEuNSAyOTIuNVEyODMgMzEwIDIzNyAzMjhRMTgxIDM1MCAxMzkuNSAzNzQuNVE5OCAzOTkgNzUuNSA0MzQuNVE1MyA0NzAgNTMgNTI0UTUzIDU4NCA4MC4wIDYyNS4wUTEwNyA2NjYgMTU4LjAgNjg3LjBRMjA5IDcwOCAyNzkgNzA4UTMzNyA3MDggMzg2LjUgNjkzLjVRNDM2IDY3OSA0NjMgNjYyTDQzNyA1OTdRNDA4IDYxNyAzNjYuNSA2MjkuMFEzMjUgNjQxIDI3OCA2NDFRMjE0IDY0MSAxNzMuMCA2MTUuMFExMzIgNTg5IDEzMiA1MzBRMTMyIDQ5MCAxNTIuMCA0NjUuMFExNzIgNDQwIDIwNy4wIDQyMy4wUTI0MiA0MDYgMjg2IDM4OFEzNDMgMzY2IDM4OC41IDM0MS41UTQzNCAzMTcgNDYxLjAgMjc4LjVRNDg4IDI0MCA0ODggMTc1UTQ4OCAxMTIgNDU4LjAgNzAuMFE0MjggMjggMzczLjAgNi41UTMxOCAtMTUgMjQyIC0xNVoiIGZpbGw9ImJsYWNrIi8+CjxnIGZpbGw9ImJsYWNrIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxNTQuNjggMCkiPgo8cGF0aCB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjAwIDE5MC43Nykgc2NhbGUoMC4yNDM3ODUgLTAuMjQzNzg1KSIgZD0iTTI0MiAtMTVRMTYxIC0xNSAxMDcuNSAzLjBRNTQgMjEgMzQgMzNMNTkgOTlRODAgODcgMTI2LjUgNzAuMFExNzMgNTMgMjQyIDUzUTMyMSA1MyAzNjQuMCA4MS41UTQwNyAxMTAgNDA3IDE3MlE0MDcgMjIwIDM4My41IDI0Ny41UTM2MCAyNzUgMzIxLjUgMjkyLjVRMjgzIDMxMCAyMzcgMzI4UTE4MSAzNTAgMTM5LjUgMzc0LjVROTggMzk5IDc1LjUgNDM0LjVRNTMgNDcwIDUzIDUyNFE1MyA1ODQgODAuMCA2MjUuMFExMDcgNjY2IDE1OC4wIDY4Ny4wUTIwOSA3MDggMjc5IDcwOFEzMzcgNzA4IDM4Ni41IDY5My41UTQzNiA2NzkgNDYzIDY2Mkw0MzcgNTk3UTQwOCA2MTcgMzY2LjUgNjI5LjBRMzI1IDY0MSAyNzggNjQxUTIxNCA2NDEgMTczLjAgNjE1LjBRMTMyIDU4OSAxMzIgNTMwUTEzMiA0OTAgMTUyLjAgNDY1LjBRMTcyIDQ0MCAyMDcuMCA0MjMuMFEyNDIgNDA2IDI4NiAzODhRMzQzIDM2NiAzODguNSAzNDEuNVE0MzQgMzE3IDQ2MS4wIDI3OC41UTQ4OCAyNDAgNDg4IDE3NVE0ODggMTEyIDQ1OC4wIDcwLjBRNDI4IDI4IDM3My4wIDYuNVEzMTggLTE1IDI0MiAtMTVaIi8+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKDEyNy43NCAxOTAuNzcpIHNjYWxlKDAuMjQzNzg1IC0wLjI0Mzc4NSkiIGQ9Ik0yNTMgLTExUTE4NyAtMTEgMTQ5LjAgMTIuMFExMTEgMzUgOTUuNSA4MS4wUTgwIDEyNyA4MCAxOTZWNjY4TDE1NSA2ODFWNTE4SDM1OFY0NTVIMTU1VjE5MFExNTUgMTM1IDE2Ny41IDEwNi4wUTE4MCA3NyAyMDMuNSA2Ni41UTIyNyA1NiAyNTkgNTZRMjk3IDU2IDMyMi41IDY1LjBRMzQ4IDc0IDM2MyA4MUwzNzkgMjBRMzY0IDExIDMyOS41IDAuMFEyOTUgLTExIDI1MyAtMTFaIi8+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKDIyMy41NSAxOTAuNzcpIHNjYWxlKDAuMjQzNzg1IC0wLjI0Mzc4NSkiIGQ9Ik0yNDEgLTExUTE4NSAtMTEgMTQxLjAgNS4wUTk3IDIxIDcyLjAgNTcuMFE0NyA5MyA0NyAxNTJRNDcgMjA5IDc1LjAgMjQ0LjVRMTAzIDI4MCAxNTIuNSAyOTYuMFEyMDIgMzEyIDI2NCAzMTJRMjkyIDMxMiAzMjMuMCAzMDcuMFEzNTQgMzAyIDM2MiAyOThWMzI4UTM2MiAzNjIgMzUzLjUgMzkzLjVRMzQ1IDQyNSAzMTkuMCA0NDUuMFEyOTMgNDY1IDI0MCA0NjVRMTg1IDQ2NSAxNTYuMCA0NTcuMFExMjcgNDQ5IDExMyA0NDRMMTAzIDUwOFExMjEgNTE2IDE1OC4wIDUyMy4wUTE5NSA1MzAgMjQ1IDUzMFEzMTYgNTMwIDM1Ny41IDUwNS4wUTM5OSA0ODAgNDE3LjUgNDM2LjVRNDM2IDM5MyA0MzYgMzM3VjEyUTQxNSA3IDM2MS4wIC0yLjBRMzA3IC0xMSAyNDEgLTExWk0yNTIgNTNRMjg3IDUzIDMxNS4wIDU1LjVRMzQzIDU4IDM2MiA2MlYyMzZRMzUyIDI0MSAzMjguMCAyNDYuMFEzMDQgMjUxIDI2NiAyNTFRMjM0IDI1MSAyMDEuMCAyNDQuMFExNjggMjM3IDE0NS41IDIxNi4wUTEyMyAxOTUgMTIzIDE1M1ExMjMgOTcgMTU4LjAgNzUuMFExOTMgNTMgMjUyIDUzWiIvPgo8cGF0aCB0cmFuc2Zvcm09InRyYW5zbGF0ZSgzNDguODYgMTkwLjc3KSBzY2FsZSgwLjI0Mzc4NSAtMC4yNDM3ODUpIiBkPSJNODQgMFY0OTRRMTEwIDUwNSAxNTUuNSA1MTYuNVEyMDEgNTI4IDI2NSA1MjhRMjg2IDUyOCAzMDYuNSA1MjUuNVEzMjcgNTIzIDM0My41IDUxOS41UTM2MCA1MTYgMzY4IDUxM0wzNTMgNDQ5UTM0NCA0NTMgMzE5LjAgNDU3LjVRMjk0IDQ2MiAyNTUgNDYyUTIxNyA0NjIgMTkyLjAgNDU2LjVRMTY3IDQ1MSAxNTkgNDQ3VjBaIi8+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQ0MS4yNSAxOTAuNzcpIHNjYWxlKDAuMjQzNzg1IC0wLjI0Mzc4NSkiIGQ9Ik0yNTMgLTExUTE4NyAtMTEgMTQ5LjAgMTIuMFExMTEgMzUgOTUuNSA4MS4wUTgwIDEyNyA4MCAxOTZWNjY4TDE1NSA2ODFWNTE4SDM1OFY0NTVIMTU1VjE5MFExNTUgMTM1IDE2Ny41IDEwNi4wUTE4MCA3NyAyMDMuNSA2Ni41UTIyNyA1NiAyNTkgNTZRMjk3IDU2IDMyMi41IDY1LjBRMzQ4IDc0IDM2MyA4MUwzNzkgMjBRMzY0IDExIDMyOS41IDAuMFEyOTUgLTExIDI1MyAtMTFaIi8+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKDUzNy4wNiAxOTAuNzcpIHNjYWxlKDAuMjQzNzg1IC0wLjI0Mzc4NSkiIGQ9Ik03MiAwUTc2IDkyIDgxLjAgMTgzLjBRODYgMjc0IDkyLjAgMzYxLjVROTggNDQ5IDEwNS4wIDUzMi41UTExMiA2MTYgMTIxIDY5M0gxOTFRMjIwIDY0NSAyNTIuNSA1ODEuNVEyODUgNTE4IDMxOC4wIDQ0OC41UTM1MSAzNzkgMzgxLjUgMzEyLjBRNDEyIDI0NSA0MzYgMTkxUTQ2MCAyNDUgNDkwLjUgMzEyLjBRNTIxIDM3OSA1NTQuMCA0NDguNVE1ODcgNTE4IDYyMC4wIDU4MS41UTY1MyA2NDUgNjgxIDY5M0g3NDdRNzU2IDYxNiA3NjMuNSA1MzIuNVE3NzEgNDQ5IDc3Ni41IDM2MS41UTc4MiAyNzQgNzg3LjUgMTgzLjBRNzkzIDkyIDc5NyAwSDcxOVE3MTUgMTAyIDcxMC41IDIwMC41UTcwNiAyOTkgNzAwLjAgMzkxLjBRNjk0IDQ4MyA2ODYgNTY1UTY3NiA1NDYgNjU0LjUgNTAyLjVRNjMzIDQ1OSA2MDYuMCA0MDIuNVE1NzkgMzQ2IDU1MS41IDI4Ny4wUTUyNCAyMjggNTAxLjUgMTc4LjBRNDc5IDEyOCA0NjcgOTlINDAwUTM4OCAxMjggMzY1LjUgMTc4LjBRMzQzIDIyOCAzMTUuNSAyODcuMFEyODggMzQ2IDI2MS4wIDQwMi41UTIzNCA0NTkgMjEyLjUgNTAyLjVRMTkxIDU0NiAxODEgNTY1UTE3MyA0ODMgMTY3LjAgMzkxLjBRMTYxIDI5OSAxNTYuNSAyMDAuNVExNTIgMTAyIDE0OCAwWiIvPgo8cGF0aCB0cmFuc2Zvcm09InRyYW5zbGF0ZSg3NDguOTEgMTkwLjc3KSBzY2FsZSgwLjI0Mzc4NSAtMC4yNDM3ODUpIiBkPSJNMjQxIC0xMVExODUgLTExIDE0MS4wIDUuMFE5NyAyMSA3Mi4wIDU3LjBRNDcgOTMgNDcgMTUyUTQ3IDIwOSA3NS4wIDI0NC41UTEwMyAyODAgMTUyLjUgMjk2LjBRMjAyIDMxMiAyNjQgMzEyUTI5MiAzMTIgMzIzLjAgMzA3LjBRMzU0IDMwMiAzNjIgMjk4VjMyOFEzNjIgMzYyIDM1My41IDM5My41UTM0NSA0MjUgMzE5LjAgNDQ1LjBRMjkzIDQ2NSAyNDAgNDY1UTE4NSA0NjUgMTU2LjAgNDU3LjBRMTI3IDQ0OSAxMTMgNDQ0TDEwMyA1MDhRMTIxIDUxNiAxNTguMCA1MjMuMFExOTUgNTMwIDI0NSA1MzBRMzE2IDUzMCAzNTcuNSA1MDUuMFEzOTkgNDgwIDQxNy41IDQzNi41UTQzNiAzOTMgNDM2IDMzN1YxMlE0MTUgNyAzNjEuMCAtMi4wUTMwNyAtMTEgMjQxIC0xMVpNMjUyIDUzUTI4NyA1MyAzMTUuMCA1NS41UTM0MyA1OCAzNjIgNjJWMjM2UTM1MiAyNDEgMzI4LjAgMjQ2LjBRMzA0IDI1MSAyNjYgMjUxUTIzNCAyNTEgMjAxLjAgMjQ0LjBRMTY4IDIzNyAxNDUuNSAyMTYuMFExMjMgMTk1IDEyMyAxNTNRMTIzIDk3IDE1OC4wIDc1LjBRMTkzIDUzIDI1MiA1M1oiLz4KPHBhdGggdHJhbnNmb3JtPSJ0cmFuc2xhdGUoODc0LjIxIDE5MC43Nykgc2NhbGUoMC4yNDM3ODUgLTAuMjQzNzg1KSIgZD0iTTg0IDBWNzYzTDE1OSA3NzZWMjkwUTE4MyAzMTQgMjEzLjAgMzQ0LjBRMjQzIDM3NCAyNzQuMCA0MDYuMFEzMDUgNDM4IDMzMi4wIDQ2Ny4wUTM1OSA0OTYgMzc4IDUxOEg0NjdRNDM3IDQ4NiAzOTYuNSA0NDQuMFEzNTYgNDAyIDMxNC41IDM1OS41UTI3MyAzMTcgMjM4IDI4M1EyNzAgMjYxIDMwNC41IDIyNy41UTMzOSAxOTQgMzczLjAgMTU1LjBRNDA3IDExNiA0MzYuNSA3Ni4wUTQ2NiAzNiA0ODcgMEg0MDBRMzcwIDUxIDMyOC4wIDEwMC41UTI4NiAxNTAgMjQyLjAgMTkxLjBRMTk4IDIzMiAxNTkgMjU3VjBaIi8+CjxwYXRoIHRyYW5zZm9ybT0idHJhbnNsYXRlKDk5Ny4zMyAxOTAuNzcpIHNjYWxlKDAuMjQzNzg1IC0wLjI0Mzc4NSkiIGQ9Ik0zMTEgLTExUTIyMCAtMTEgMTYzLjUgMjQuMFExMDcgNTkgODAuNSAxMjAuMFE1NCAxODEgNTQgMjU5UTU0IDM1MCA4Ny4wIDQxMC4wUTEyMCA0NzAgMTcyLjUgNTAwLjBRMjI1IDUzMCAyODMgNTMwUTM0OCA1MzAgMzk1LjUgNTAyLjVRNDQzIDQ3NSA0NjkuMCA0MTguNVE0OTUgMzYyIDQ5NSAyNzVRNDk1IDI2OCA0OTQuNSAyNTguNVE0OTQgMjQ5IDQ5MyAyNDFIMTMyUTEzNiAxNTMgMTc5LjUgMTA0LjVRMjIzIDU2IDMxNSA1NlEzNjYgNTYgMzk4LjUgNjUuNVE0MzEgNzUgNDQ1IDgyTDQ1OCAxOVE0NDQgMTEgNDAzLjUgMC4wUTM2MyAtMTEgMzExIC0xMVpNMTM0IDMwMkg0MTlRNDE4IDM1MyA0MDIuMCAzODkuNVEzODYgNDI2IDM1Ni41IDQ0NS41UTMyNyA0NjUgMjg0IDQ2NVEyNDAgNDY1IDIwNy4wIDQ0Mi4wUTE3NCA0MTkgMTU1LjUgMzgyLjBRMTM3IDM0NSAxMzQgMzAyWiIvPgo8cGF0aCB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxMTMxLjkwIDE5MC43Nykgc2NhbGUoMC4yNDM3ODUgLTAuMjQzNzg1KSIgZD0iTTg0IDBWNDk0UTExMCA1MDUgMTU1LjUgNTE2LjVRMjAxIDUyOCAyNjUgNTI4UTI4NiA1MjggMzA2LjUgNTI1LjVRMzI3IDUyMyAzNDMuNSA1MTkuNVEzNjAgNTE2IDM2OCA1MTNMMzUzIDQ0OVEzNDQgNDUzIDMxOS4wIDQ1Ny41UTI5NCA0NjIgMjU1IDQ2MlEyMTcgNDYyIDE5Mi4wIDQ1Ni41UTE2NyA0NTEgMTU5IDQ0N1YwWiIvPgo8L2c+Cjwvc3ZnPg=='

export function LearnHouseEmail({
  accentColor,
  heading,
  subtitle,
  body,
  bulletPoints,
  card,
  transition,
  cta,
}: LearnHouseEmailProps) {
  return (
    <Html>
      <Head />
      <Preview>{subtitle}</Preview>
      <Body style={{ backgroundColor: '#f5f5f5', fontFamily: 'Inter, Helvetica, Arial, sans-serif', margin: 0, padding: '24px 0' }}>
        <Container style={{ backgroundColor: '#ffffff', borderRadius: 16, overflow: 'hidden', maxWidth: 560, margin: '0 auto', border: '1px solid #eee' }}>
          {/* Accent bar */}
          <div style={{ height: 6, backgroundColor: accentColor }} />

          <Section style={{ padding: '32px 40px 8px' }}>
            <Img src={LOGO_URL} alt="StartMaker" height={28} style={{ marginBottom: 24 }} />
            <Heading style={{ fontSize: 24, fontWeight: 800, color: '#171717', margin: '0 0 8px', lineHeight: 1.25 }}>
              {heading}
            </Heading>
            <Text style={{ fontSize: 15, color: '#525252', margin: 0, lineHeight: 1.5 }}>{subtitle}</Text>
          </Section>

          {body && (
            <Section style={{ padding: '8px 40px' }}>
              <Text style={{ fontSize: 14, color: '#404040', margin: 0, lineHeight: 1.6 }}>{body}</Text>
            </Section>
          )}

          {card && (
            <Section style={{ padding: '8px 40px' }}>
              <div style={{ border: `1px solid ${card.color}22`, backgroundColor: `${card.color}0d`, borderRadius: 12, padding: '16px 18px' }}>
                <Text style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5, color: card.color, margin: '0 0 4px' }}>
                  {card.label}
                </Text>
                <Text style={{ fontSize: 18, fontWeight: 700, color: '#171717', margin: 0 }}>{card.title}</Text>
                {card.caption && <Text style={{ fontSize: 12, color: '#737373', margin: '2px 0 0' }}>{card.caption}</Text>}
              </div>
            </Section>
          )}

          {transition && (
            <Section style={{ padding: '8px 40px' }}>
              <div style={{ display: 'flex', gap: 12, alignItems: 'stretch' }}>
                <div style={{ flex: 1, border: `1px solid ${transition.fromColor}22`, backgroundColor: `${transition.fromColor}0d`, borderRadius: 12, padding: '12px 14px' }}>
                  <Text style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', color: transition.fromColor, margin: '0 0 2px' }}>{transition.fromLabel}</Text>
                  <Text style={{ fontSize: 16, fontWeight: 700, color: '#171717', margin: 0 }}>{transition.fromValue}</Text>
                </div>
                <div style={{ flex: 1, border: `1px solid ${transition.toColor}22`, backgroundColor: `${transition.toColor}0d`, borderRadius: 12, padding: '12px 14px' }}>
                  <Text style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', color: transition.toColor, margin: '0 0 2px' }}>{transition.toLabel}</Text>
                  <Text style={{ fontSize: 16, fontWeight: 700, color: '#171717', margin: 0 }}>{transition.toValue}</Text>
                </div>
              </div>
            </Section>
          )}

          {bulletPoints && bulletPoints.length > 0 && (
            <Section style={{ padding: '8px 40px' }}>
              {bulletPoints.map((point, i) => (
                <Text key={i} style={{ fontSize: 14, color: '#404040', margin: '0 0 6px', lineHeight: 1.5 }}>
                  <span style={{ color: accentColor, fontWeight: 700, marginRight: 8 }}>•</span>
                  {point}
                </Text>
              ))}
            </Section>
          )}

          {cta && (
            <Section style={{ padding: '16px 40px 8px' }}>
              <a
                href={cta.href}
                style={{ display: 'inline-block', backgroundColor: accentColor, color: '#ffffff', fontWeight: 700, fontSize: 14, padding: '11px 22px', borderRadius: 10, textDecoration: 'none' }}
              >
                {cta.label}
              </a>
            </Section>
          )}

          <Hr style={{ borderColor: '#eee', margin: '24px 40px 0' }} />
          <Section style={{ padding: '16px 40px 32px' }}>
            <Text style={{ fontSize: 12, color: '#a3a3a3', margin: 0 }}>
              StartMaker — the open-source learning platform.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  )
}

export default LearnHouseEmail
