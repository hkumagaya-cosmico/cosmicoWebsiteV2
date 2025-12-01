export default async function handler(req, res) {
  // CORS設定
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  try {
    // req.bodyは既にパースされている場合と文字列の場合がある
    const body = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
    const { name, company, email, message } = body;

    // バリデーション
    if (!name || !email || !message) {
      return res.status(400).json({ error: '必須項目が入力されていません' });
    }

    // メール本文を作成
    const emailBody = `
お問い合わせがありました。

【お名前】
${name}

【会社名】
${company || '未入力'}

【メールアドレス】
${email}

【お問い合わせ内容】
${message}

---
このメールは、Cosmicoウェブサイトのお問い合わせフォームから送信されました。
`;

    // Resend APIを使用してメール送信
    const RESEND_API_KEY = process.env.RESEND_API_KEY;
    
    if (!RESEND_API_KEY) {
      // 環境変数が設定されていない場合は、コンソールに出力（開発用）
      console.log('=== お問い合わせメール ===');
      console.log(emailBody);
      console.log('========================');
      
      return res.status(200).json({ 
        success: true, 
        message: 'お問い合わせを受け付けました（開発モード）' 
      });
    }

    // Resend APIでメール送信
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RESEND_API_KEY}`,
      },
      body: JSON.stringify({
        from: 'Cosmico <noreply@cosmicoai.com>',
        to: ['h.kumagaya@cosmicoai.com'],
        reply_to: email,
        subject: `【Cosmico】お問い合わせ: ${name}様より`,
        text: emailBody,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Resend API Error:', errorData);
      return res.status(500).json({ error: 'メール送信に失敗しました' });
    }

    const data = await response.json();
    return res.status(200).json({ 
      success: true, 
      message: 'お問い合わせありがとうございます。内容を確認の上、担当者よりご連絡いたします。' 
    });

  } catch (error) {
    console.error('Error sending email:', error);
    return res.status(500).json({ error: 'サーバーエラーが発生しました' });
  }
}

